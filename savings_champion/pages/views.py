# coding=utf-8
from collections import defaultdict
import datetime
from itertools import chain
from math import log10
from operator import attrgetter
import os

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.forms.models import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.templatetags.static import static
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render_to_response, redirect, render
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.core.mail import EmailMultiAlternatives

from django.views.decorators.cache import never_cache

from common.accounts.utils import create_stage_one_profile
from common.tasks import add_to_campaign_monitor, send_email, analytics, update_subscription_on_email_service
from common.utils import record_referral_signup
from concierge.models import AdviserQueue, ConciergeUserNotes
from concierge.tasks import register_enquiry
from pages.models import Article, BlogItem, RateAlert, Award, AwardCategory, Petition, PressAppearance, \
    PressAppearancePublication, SavingsPriorityListOptionSignup, FiftyPoundChallengeAccount, ProductFAQ, FactFindAccount
from pages.models import ParentPage, ChildPage, FAQ
from pages.forms import ConciergeSignupForm, ArticleCommentForm, BlogCommentForm, PetitionForm, PetitionEmailForm, \
    SevenPitfallsForm, IHTGuideForm, FilterForm, NISAGuideForm, SavingsPriorityListForm, SavingsPriorityProductForm, \
    SavingsPriorityListOptionForm, FiftyPoundChallengeForm, FiftyPoundChallengeAccountForm, \
    FiftyPoundChallengeAccountFormHelper, ProductQuestionaireForm, TheBiggestMistakeForm, FactFindForm, \
    FactFindAccountForm, FactFindAccountFormHelper, PensionOptionsForm, MindfulMoneyHealthcheckForm, \
    MoneyToTheMassesForm, ChallengerBankGuideForm, FBIHTGuideForm, OBIHTGuideForm, IHTSqueezePageForm, \
    PSASqueezePageForm, HighWorthSqueezePageForm
from products.models import Provider
from common.models import CampaignsSignup, Referrer
from pages.signupformutils import get_post_form

User = get_user_model()


def news_index(request, template_file='news/index.html'):
    context = RequestContext(request)
    context['heading'] = "All News"

    if request.user.is_staff:
        articles = Article.objects.filter(type__iexact="Article")
        ask_the_experts = BlogItem.objects.filter(genre='Ask the experts')
    else:
        articles = Article.objects.filter(publish_date__lte=datetime.datetime.now(),
                                          type__iexact="Article",
                                          outbrain_content=False)
        ask_the_experts = BlogItem.objects.filter(genre='Ask the experts', publish_date__lte=datetime.datetime.now())

    posts = sorted(chain(articles, ask_the_experts),
                   key=attrgetter('publish_date'), reverse=True)

    context['news_index'] = True
    context['feed_url'] = reverse('rss_feed_all')
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')

    try:
        paginated_posts = paginator.page(page)
    except (TypeError, PageNotAnInteger, EmptyPage):
        paginated_posts = paginator.page(1)

    # context['posts'] = paginated_posts
    context['max_pages'] = paginator.num_pages
    return render_to_response(template_file, {"posts": paginated_posts},
                              context_instance=context)


def article_index(request, template_file='news/index.html'):
    context = RequestContext(request)
    context['heading'] = "Expert Analysis"
    if request.user.is_staff:
        articles = Article.objects.filter(type__iexact="Article").order_by('-publish_date')
    else:
        articles = Article.objects.filter(publish_date__lte=datetime.datetime.now(),
                                          type__iexact="Article",
                                          outbrain_content=False
                                          ).order_by(
            '-publish_date')

    paginator = Paginator(articles, 6)
    page = request.GET.get('page')

    try:
        paginated_posts = paginator.page(page)
    except (TypeError, PageNotAnInteger, EmptyPage):
        paginated_posts = paginator.page(1)
    context['feed_url'] = reverse('rss_feed_articles')
    context['article_index'] = True
    context['max_pages'] = paginator.num_pages
    return render_to_response(template_file, {"posts": paginated_posts},
                              context_instance=context)


def blog_index(request, template_file='news/index.html'):
    context = RequestContext(request)
    context['heading'] = "Ask Anna"
    if request.user.is_staff:
        blogs = BlogItem.objects.filter(genre='Ask the experts').order_by('-publish_date')
    else:
        blogs = BlogItem.objects.filter(publish_date__lte=datetime.datetime.now(), genre='Ask the experts').order_by(
            '-publish_date')
    paginator = Paginator(blogs, 6)
    page = request.GET.get('page')

    try:
        paginated_posts = paginator.page(page)
    except (TypeError, PageNotAnInteger, EmptyPage):
        paginated_posts = paginator.page(1)

    context['blog_index'] = True
    context['feed_url'] = reverse('rss_feed_blogs')
    context['max_pages'] = paginator.num_pages
    return render_to_response(template_file, {"posts": paginated_posts},
                              context_instance=context)


def ratealert_index(request, template_file='news/ra_index.html'):
    context = RequestContext(request)
    context['heading'] = 'Archive'
    if request.user.is_staff:
        ratealerts = RateAlert.objects.all().order_by('-publish_date')
    else:
        ratealerts = RateAlert.objects.filter(publish_date__lte=datetime.datetime.now()).order_by('-publish_date')

    paginator = Paginator(ratealerts, 6)
    page = request.GET.get('page')

    try:
        paginated_posts = paginator.page(page)
    except (TypeError, PageNotAnInteger, EmptyPage):
        paginated_posts = paginator.page(1)

    context['max_pages'] = paginator.num_pages
    return render_to_response(template_file, {"posts": paginated_posts},
                              context_instance=context)


@never_cache
def view_article(request, post_slug, template_file='news/post.html'):
    context = RequestContext(request)

    post = get_object_or_404(Article, slug=post_slug)

    context['comments'] = post.articlecomment_set.filter(approved=True).order_by('comment_date')

    data = {'user': request.user.id,
            'post': post.id,
            'article_comment': post,
            'comment_date': datetime.datetime.now()
            }

    context['form'] = ArticleCommentForm(initial=data)
    signupform = get_post_form(post)
    if signupform:
        context['signupform'] = signupform
    if post.show_isa_tool:
        context['providers'] = Provider.objects.all()
    context['post'] = post
    context['comments_enabled'] = True
    return render_to_response(template_file, context)


@never_cache
def view_blog(request, post_slug, template_file='news/post.html'):
    context = RequestContext(request)

    post = get_object_or_404(BlogItem, slug=post_slug)
    context['comments'] = post.blogcomment_set.filter(approved=True).order_by('comment_date')

    data = {'user': request.user.id,
            'post': post.id,
            'blog_comment': post,
            'comment_date': datetime.datetime.now()
            }

    context['form'] = BlogCommentForm(initial=data)

    signupform = get_post_form(post)
    if signupform:
        context['signupform'] = signupform

    context['post'] = post
    context['comments_enabled'] = True
    return render_to_response(template_file, context)


@never_cache
def view_ask_the_experts(request, post_slug, template_file='news/post.html'):
    context = RequestContext(request)

    post = get_object_or_404(BlogItem, slug=post_slug)
    context['comments'] = post.blogcomment_set.filter(approved=True).order_by('comment_date')

    data = {'user': request.user.id,
            'post': post.id,
            'blog_comment': post,
            'comment_date': datetime.datetime.now()
            }

    context['form'] = BlogCommentForm(initial=data)

    signupform = get_post_form(post)
    if signupform:
        context['signupform'] = signupform

    context['post'] = post
    context['comments_enabled'] = True
    return render_to_response(template_file, context)


@never_cache
def view_ratealert(request, rateslug, template_file='news/post.html'):
    context = RequestContext(request)

    try:
        post = RateAlert.objects.get(slug=rateslug)
    except RateAlert.DoesNotExist:
        messages.error(request,
                       'Rate alert not found at this address, you have been redirected to the latest rate alert')
        return redirect('view_ratealert_overview')
    except RateAlert.MultipleObjectsReturned:
        post = RateAlert.objects.filter(slug=rateslug)[0]

    context['post'] = post

    return render_to_response(template_file, context)


@never_cache
def view_ratealert_overview(request, template_file='news/ra_overview.html'):
    context = RequestContext(request)

    today = datetime.datetime.now()
    post = RateAlert.objects.exclude(publish_date__gt=today).latest('publish_date')

    context['post'] = post

    return render_to_response(template_file, context)


def concierge_signup(request, intermediary=False, business=False, charity=False, video=False, video_campaign=False,
                     trust=False, template_file='concierge/signup.html'):
    context = RequestContext(request)

    # set the video autoplay status, default 1
    autoplay = '1'
    if 'autoplay' in request.GET:
        autoplay = request.GET['autoplay']

    data = {}
    if video:
        data = {'source': 'Video'}
    if video_campaign:
        data = {'source': 'Video 0.1%'}

    if business:
        data = {'source': 'Business Concierge'}
    if intermediary:
        data = {'source': 'Intermediary'}
    if trust:
        data = {'source': 'Trust Concierge'}
    if charity:
        data = {'source': 'Charity Concierge'}

    context['autoplay'] = autoplay
    context['form'] = ConciergeSignupForm(initial=data)

    return render_to_response(template_file, context)


def concierge_faq(request, template_file='concierge/faq.html'):
    context = RequestContext(request)
    context['form'] = ConciergeSignupForm()
    context['faqs'] = FAQ.objects.get(title="Concierge").faqblock_set.all().order_by('order')
    return render_to_response(template_file, context)


def concierge_thankyou(request, template_file="concierge/thankyou.html"):
    context = RequestContext(request)
    if request.method == "POST":
        form = ConciergeSignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if not CampaignsSignup.objects.filter(email=email).exists():
                if 'referer' in request.session:
                    referer = Referrer.objects.get(pk=request.session['referer']).name
                else:
                    referer = '(Direct)'
                analytics.delay('event', 'Concierge', 'Signup', referer)
                text_email = get_template('core/concierge_signup_email.txt')
                c = Context({'name': form.cleaned_data.get('name'),
                             'email': email,
                             'telephone': form.cleaned_data.get('telephone'),
                             'alt_telephone': form.cleaned_data.get('alt_telephone'),
                             'best_call_time': form.cleaned_data.get('timetocall'),
                             'source': form.cleaned_data.get('source', None),
                             })

                text_content = text_email.render(c)

                subject, from_email = "New Concierge Signup", "savings.champion@savingschampion.co.uk"
                msg = EmailMultiAlternatives(subject, text_content, from_email, ["concierge@savingschampion.co.uk"])
                msg.send()
                saved_data = form.save()
                try:
                    AdviserQueue(name=saved_data.name, email=saved_data.email,
                                 telephone=saved_data.telephone, source=saved_data.source,
                                 preferred_contact_time=form.cleaned_data.get('timetocall')).save()

                    AdviserQueue.add_to_queue(email=saved_data.email,
                                              first_name=saved_data.name,
                                              last_name='.',
                                              lead_source=saved_data.source,
                                              telephone_number=saved_data.telephone,
                                              preferred_contact_time=form.cleaned_data.get('timetocall')
                                              )
                except IntegrityError:
                    if AdviserQueue.new_lead(saved_data.email):
                        adviser_queue = AdviserQueue.objects.get(email=saved_data.email)
                        if adviser_queue.status in [2, 8, 9, 10] and adviser_queue.adviser is not None:
                            adviser_queue.adviser = None
                        adviser_queue.interaction_started = datetime.datetime.now()
                        adviser_queue.save()

                        AdviserQueue.add_to_queue(email=saved_data.email,
                                                  first_name=saved_data.name,
                                                  last_name='.',
                                                  lead_source=saved_data.source,
                                                  telephone_number=saved_data.telephone,
                                                  preferred_contact_time=form.cleaned_data.get('timetocall')
                                                  )

                user, user_created, record_stats = create_stage_one_profile(request, email=saved_data.email,
                                                                            source=saved_data.source,
                                                                            send_activation=False, login_user=False)
                record_referral_signup(request, user, user_created, 'concierge_enquiry')
            return redirect('concierge_thankyou')

    return render_to_response(template_file, context)


def concierge_more(request, template_file='concierge/more.html'):
    context = RequestContext(request)

    context['form'] = ConciergeSignupForm()

    return render_to_response(template_file, context)


def page_controller(request, parent, template_file='pages/page.html', left_nav="pages/leftnav.html"):
    context = RequestContext(request)
    parent = parent.replace('/', '')
    parentpage = get_object_or_404(ParentPage, slug=parent)
    context['title'] = parentpage.title
    context['leftnav'] = left_nav
    children = parentpage.childpage_set.all().order_by('order')
    if len(children) > 0:
        context['childpages'] = children
        child = children[0]
        context['activeslug'] = child.slug
        context['subtitle'] = child.title
        context['body'] = child.body
        context['meta'] = child.meta
    else:
        context['body'] = parentpage.body
        context['meta'] = parentpage.meta

    return render_to_response(template_file, context)


def child_page_controller(request, parent, child, template_file='pages/page.html', left_nav="pages/leftnav.html"):
    context = RequestContext(request)
    # not sure if it is better practice to have urls with / by default (like I am doing)
    # or let Django add the trailing / automatically
    # for now we will strip out the /

    parent = parent.replace('/', '')
    child = child.replace('/', '')
    parentpage = get_object_or_404(ParentPage, slug=parent)
    childpage = get_object_or_404(ChildPage, slug=child)
    context['leftnav'] = left_nav
    children = parentpage.childpage_set.exclude(slug='contact-us').order_by('order')

    if parentpage:
        context['title'] = parentpage.title
    else:
        context['title'] = childpage.title
    context['activeslug'] = childpage.slug
    context['subtitle'] = childpage.title
    context['meta'] = childpage.meta
    context['body'] = childpage.body
    if len(children) > 0:
        context['childpages'] = children

    return render_to_response(template_file, context)


def add_article_comment(request):
    if request.method == "POST":
        form = ArticleCommentForm(request.POST)
        if form.is_valid():
            form.save()
            post = form.cleaned_data.get('article_comment')
            comment = post.articlecomment_set.filter(comment=form.cleaned_data.get('comment'))[0]
            send_mail('New comment posted on %s' % post.title,
                      'The comment text is: %s \n Click to approve: https://savingschampion.co.uk%s' % (
                          form.cleaned_data.get('comment'), comment.build_approve_url()),
                      'savings.champion@savingschampion.co.uk',
                      ['info@savingschampion.co.uk'], fail_silently=False)
            messages.success(request,
                             'Thank you for taking the time to comment, we will email you when your comment has been added to this article')

            return HttpResponse(status=200)
        return HttpResponse(status=500, content=form.errors)
    else:
        return redirect('ajax_required')


def add_blog_comment(request):
    if request.method == "POST":
        form = BlogCommentForm(request.POST)
        if form.is_valid():
            form.save()

            post = form.cleaned_data.get('blog_comment')
            comment = post.blogcomment_set.filter(comment=form.cleaned_data.get('comment'))[0]
            send_mail('New comment posted on %s' % post.title,
                      'The comment text is: %s \n Click to approve: https://%s%s' % (
                          form.cleaned_data.get('comment'), request.domain, comment.build_approve_url()),
                      'savings.champion@savingschampion.co.uk',
                      ['info@savingschampion.co.uk'], fail_silently=False)
            messages.success(request,
                             'Thank you for taking the time to comment, we will email you when your comment has been added to this blog post')

            return HttpResponse(status=200)
        return HttpResponse(status=500, content=form.errors)
    else:
        return redirect('ajax_required')


def comment_success(request, template_file='news/commentsuccess.html'):
    context = RequestContext(request)

    return render_to_response(template_file, context)


def advice_index(request, template_file='advice/index.html'):
    context = RequestContext(request)
    context['heading'] = "Guides"

    if request.user.is_staff:
        articles = Article.objects.filter(type="guide")
    else:
        articles = Article.objects.filter(publish_date__lte=datetime.datetime.now(), type="guide")

    posts = articles.order_by('guide_section', '-publish_date')

    return render_to_response(template_file, {"posts": posts},
                              context_instance=context)


def awards(request, year=None):
    awarded_years = Award.objects.all().dates('awarded_date', 'year', order='DESC')

    if year is None:
        year = awarded_years.first().year

    awards = Award.objects.filter(awarded_date__year=year)
    award_categories = AwardCategory.objects.filter(award__in=awards).distinct()
    award_data = defaultdict(dict)
    for award in awards:
        award_data[award.category.title][award.ranking] = {'provider': award.provider, 'award': award,
                                                           'product': award.product}
    award_image_winner = static("img/awards/%s-Winner.png" % year)
    award_image_hc = static("img/awards/%s-Highly Commended.png" % year)
    return render(request, 'awards/awards.html', {'awards': awards, 'award_categories': award_categories,
                                                  'award_image_winner': award_image_winner,
                                                  'award_image_hc': award_image_hc, 'year': int(year),
                                                  'awarded_years': awarded_years, 'award_data': award_data
                                                  })


def petition(request):
    form = PetitionForm()
    petition_count = Petition.objects.count()
    if petition_count < 1:
        petition_count = 1
    petition_target = petition_count + 10 ** int(log10(abs(petition_count)))
    if request.method == "POST":
        form = PetitionForm(request.POST)
        if form.is_valid():
            petition_record = form.save()
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'Petition', 'Signup', referer)
            create_profile_output = create_stage_one_profile(request=request, email=petition_record.email,
                                                             source='petition_signup', send_activation=False,
                                                             login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='petition')

            update_subscription_on_email_service.delay(petition_record.email, interest_group=u'Petition')

            text_email = get_template('petition/petition_email.txt')
            c = Context({'first_name': petition_record.first_name,
                         'referer_id': petition_record.pk,
                         })
            text_content = text_email.render(c)
            msg = EmailMultiAlternatives(
                'Thanks for supporting our campaign to help the millions of savers suffering with record low interest rates',
                text_content,
                'savings.champion@savingschampion.co.uk',
                (petition_record.email,))
            guide_path = os.path.join(settings.STATIC_ROOT, 'doc', 'petition',
                                      'letter_to_george_osborne.pdf')
            msg.attach_file(guide_path)
            msg.send()

            return redirect('petition_thank_you')
    return render(request, 'petition/petition_form.html', {'form': form, 'petition_target': petition_target,
                                                           'petition_count': petition_count})


def petition_thank_you(request):
    share_url = 'https://savingschampion.co.uk%s' % (reverse('petition'))
    form = PetitionEmailForm(initial={'subject': 'Please sign this petition for me',
                                      'body': 'I found this petition online and thought it may be of interest.\n\nI decided to share it with you because this is an important issue that needs to be addressed.\n\nYou can see the petition here, %s' % share_url})
    return render(request, 'petition/petition_thank_you.html', {'form': form, 'share_url': share_url})


def seven_pitfalls_for_savers_signup(request):
    form = SevenPitfallsForm()
    if request.method == "POST":
        form = SevenPitfallsForm(request.POST)
        if form.is_valid():
            saved_data = form.save()
            try:
                AdviserQueue(name=saved_data.name, email=saved_data.email,
                             telephone=saved_data.phone, source='7 Pitfalls').save()
                AdviserQueue.add_to_queue(email=saved_data.email,
                                          first_name=saved_data.name,
                                          last_name='.',
                                          lead_source='7 Pitfalls',
                                          telephone_number=saved_data.phone)
            except IntegrityError:
                if AdviserQueue.new_lead(saved_data.email):
                    adviser_queue = AdviserQueue.objects.get(email=saved_data.email)
                    if adviser_queue.status in [2, 8, 9, 10] and adviser_queue.adviser is not None:
                        adviser_queue.adviser = None
                    adviser_queue.interaction_started = datetime.datetime.now()
                    adviser_queue.save()
                    AdviserQueue.add_to_queue(email=saved_data.email,
                                              first_name=saved_data.name,
                                              last_name='.',
                                              lead_source='7 Pitfalls',
                                              telephone_number=saved_data.phone)
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', '7 Pitfalls', 'Signup', referer)
            create_profile_output = create_stage_one_profile(request=request, email=saved_data.email,
                                                             source='seven_pitfalls_signup', send_activation=False,
                                                             login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
                user.first_name = saved_data.name
                user.profile.telephone = saved_data.phone
                user.profile.save()
                user.save()
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='seven_pitfalls')
            text_email = get_template('seven_pitfalls/email_content.txt')
            c = Context({'name': saved_data.name})
            text_content = text_email.render(c)
            send_email(
                subject='Seven pitfalls for larger savers',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=(saved_data.email,),
            )
            text_email = get_template('seven_pitfalls/concierge_email_content.txt')
            c = Context({'name': saved_data.name,
                         'email': saved_data.email,
                         'phone': saved_data.phone})
            text_content = text_email.render(c)
            send_email(
                subject='Seven Pitfalls Signup',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=('concierge@savingschampion.co.uk',),
            )

            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'Seven Pitfalls Guide')

            return redirect('seven_pitfalls_for_savers_thankyou')
    return render(request, 'seven_pitfalls/signup_form.html', {'form': form})


def seven_pitfalls_for_savers_thankyou(request):
    return render(request, 'seven_pitfalls/thankyou.html')


def iht_guide_signup(request, context=None):
    if context is None:
        context = {'facebook': False}
    form = IHTGuideForm()
    if request.method == "POST":
        form = IHTGuideForm(request.POST)
        if form.is_valid():
            saved_data = form.save()
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'IHT Guide', 'Signup', referer)
            create_profile_output = create_stage_one_profile(request=request, email=saved_data.email,
                                                             source='iht_guide_signup', send_activation=False,
                                                             login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
                user.first_name = saved_data.name
                user.profile.telephone = saved_data.phone
                user.profile.save()
                user.save()
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='iht_guide')
            text_email = get_template('iht_guide/email_content.txt')
            c = Context({'name': saved_data.name})
            text_content = text_email.render(c)
            # send_email(
            #     subject='IHT Guide',
            #     message=text_content,
            #     from_email='savings.champion@savingschampion.co.uk',
            #     recipient_list=(saved_data.email,),
            # )
            text_email = get_template('iht_guide/concierge_email_content.txt')
            c = Context({'name': saved_data.name,
                         'email': saved_data.email,
                         'phone': saved_data.phone})
            text_content = text_email.render(c)
            send_email(
                subject='IHT Guide Signup',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=('iht@savingschampion.co.uk',)  # 'leads@tpollp.com',
            )
            from common.tasks import update_subscription_on_email_service
            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'IHT Guide')
            AdviserQueue.add_to_queue(email=saved_data.email,
                                      first_name=saved_data.name,
                                      last_name='.',
                                      lead_source='iht_guide',
                                      telephone_number=saved_data.phone)
            return redirect('iht_guide_thankyou')
    context['form'] = form
    return render(request, 'iht_guide/signup_form.html', context)


def iht_guide_thankyou(request, context=None):
    if context is None:
        context = {'facebook': False}
    return render(request, 'iht_guide/thank_you.html', context)


def budget_summary_thankyou(request):
    return render(request, 'budget_summary/thankyou.html')


def press_appearances(request, context=None):
    if context is None:
        context = {}
    all_press = PressAppearance.objects.all().select_related('publication')

    if request.method == 'GET':
        if 'publication_filter' in request.GET:
            press_appearance_publication = get_object_or_404(PressAppearancePublication,
                                                             pk=request.GET['publication_filter'])
            all_press = all_press.filter(publication=press_appearance_publication)

    context['filter_form'] = FilterForm()

    parentpage = get_object_or_404(ParentPage, slug='press')
    context['title'] = parentpage.title
    children = parentpage.childpage_set.all().order_by('order')
    if len(children) > 0:
        context['childpages'] = children
        child = children[0]
        context['activeslug'] = child.slug
        context['subtitle'] = child.title
        context['body'] = child.body
        context['meta'] = child.meta
    else:
        context['body'] = parentpage.body
        context['meta'] = parentpage.meta

    context['publishers'] = PressAppearancePublication.objects.all()

    context['newspaper_press'] = all_press.filter(publication_type=1)

    context['radio_press'] = all_press.filter(publication_type=2)

    context['tv_press'] = all_press.filter(publication_type=3)

    return render(request, 'our_press/all_press.html', context)


def press_appearances_ajax(request, context=None):
    if context is None:
        context = {}
    all_press = PressAppearance.objects.all()

    if request.method == 'GET':
        if 'publication_filter' in request.GET:
            press_appearance_publication = get_object_or_404(PressAppearancePublication,
                                                             pk=request.GET['publication_filter'])
            all_press = all_press.filter(publication=press_appearance_publication)

    context['newspaper_press'] = all_press.filter(publication_type=1)

    context['radio_press'] = all_press.filter(publication_type=2)

    context['tv_press'] = all_press.filter(publication_type=3)

    return render(request, 'our_press/ajax_press.html', context)


def nisa_savings_guide_signup(request):
    form = NISAGuideForm()
    if request.method == "POST":
        form = NISAGuideForm(request.POST)
        if form.is_valid():
            saved_data = form.save()
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'NISA Guide', 'Signup', referer)
            create_stage_one_profile(request=request, email=saved_data.email, source='nisa_guide_signup',
                                     send_activation=False, login_user=False)
            text_email = get_template('nisa_guide/email_content.txt')
            c = Context({'name': saved_data.name})
            text_content = text_email.render(c)
            send_email(
                subject='NISA Guide',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=(saved_data.email,),
            )

            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'NISA Guide')

            return redirect('nisa_savings_guide_thankyou')
    return render(request, 'nisa_guide/signup_form.html', {'form': form})


def nisa_savings_guide_thankyou(request):
    return render(request, 'nisa_guide/thankyou.html')


def savings_priority_list_signup(request):
    form = SavingsPriorityListForm()
    if request.method == "POST":
        form = SavingsPriorityListForm(request.POST)
        if form.is_valid():
            saved_data = form.save()
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'Savings Priority List', 'Signup', referer)
            create_profile_output = create_stage_one_profile(request=request, email=saved_data.email,
                                                             source='savings_priority_list_signup',
                                                             send_activation=False, login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='savings_priority_list')
            text_email = get_template('savings_priority_list/email_content.txt')
            c = Context({'name': saved_data.name})
            text_content = text_email.render(c)
            send_email(
                subject='Savings Priority List',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=(saved_data.email,),
            )

            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'Savings Priority List')

            return savings_priority_list_thankyou(request)
    return render(request, 'savings_priority_list/signup_form.html', {'form': form})


def savings_priority_list_thankyou(request):
    return render(request, 'savings_priority_list/thankyou.html')


@login_required
def savings_priority_list_options(request, context=None):
    if context is None:
        context = {}

    object, _ = SavingsPriorityListOptionSignup.objects.get_or_create(user=request.user)

    form = SavingsPriorityListOptionForm(instance=object)

    if request.method == 'POST':
        form = SavingsPriorityListOptionForm(request.POST, instance=object)
        if form.is_valid():
            form.save()

    context['form'] = form

    return render(request, 'savings_priority_list/options.html', context)


def vanquis_3_signup(request):
    form = SavingsPriorityProductForm()
    if request.method == "POST":
        form = SavingsPriorityProductForm(request.POST)
        if form.is_valid():
            saved_data = form.save()
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'Savings Priority List', 'Signup', referer)
            create_profile_output = create_stage_one_profile(request=request, email=saved_data.email,
                                                             source='savings_priority_list_signup',
                                                             send_activation=False, login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output

            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='savings_priority_list')
            text_email = get_template('savings_priority_list/email_content.txt')
            c = Context({'name': saved_data.name})
            text_content = text_email.render(c)
            send_email(
                subject='Savings Priority List',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=(saved_data.email,),
            )
            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'Vanquis Product')

            return vanquis_3_thankyou(request)
        return HttpResponse(status=500)
    return render(request, 'vanquis_3/signup_form.html', {'form': form})


def vanquis_3_thankyou(request):
    return render(request, 'vanquis_3/thankyou.html')


def trust_concierge(request, context=None):
    if context is None:
        context = {}

    return render(request, 'trust_concierge/info.html')


def fifty_pound_challenge_signup(request):
    form = FiftyPoundChallengeForm()
    FiftyPoundChallengeAccountFormset = modelformset_factory(FiftyPoundChallengeAccount,
                                                             form=FiftyPoundChallengeAccountForm)
    account_form = FiftyPoundChallengeAccountFormset(queryset=FiftyPoundChallengeAccount.objects.none(),
                                                     prefix='accounts')
    account_form_helper = FiftyPoundChallengeAccountFormHelper()
    end_date = datetime.datetime.now() + datetime.timedelta(weeks=2)
    if request.method == "POST":
        form = FiftyPoundChallengeForm(request.POST)
        account_form = FiftyPoundChallengeAccountFormset(request.POST, prefix='accounts')
        if form.is_valid():
            saved_data = form.save()
            if account_form.is_valid():
                accounts = account_form.save(commit=False)
                for account in accounts:
                    account.challenge_signup = saved_data
                    if account.rate is not None and account.amount is not None:
                        account.save()
            else:
                accounts = []
            try:
                adviser_queue = AdviserQueue(name=saved_data.name, email=saved_data.email,
                                             telephone=saved_data.phone, source='50 Pound Challenge').save()
                AdviserQueue.add_to_queue(email=saved_data.email,
                                          first_name=saved_data.name,
                                          last_name='.',
                                          lead_source='50 Pound Challenge',
                                          telephone_number=saved_data.phone)
            except IntegrityError:
                if AdviserQueue.new_lead(saved_data.email):
                    adviser_queue = AdviserQueue.objects.get(email=saved_data.email)
                    if adviser_queue.status in [2, 8, 9, 10] and adviser_queue.adviser is not None:
                        adviser_queue.adviser = None
                    adviser_queue.interaction_started = datetime.datetime.now()
                    adviser_queue.save()
                    AdviserQueue.add_to_queue(email=saved_data.email,
                                              first_name=saved_data.name,
                                              last_name='.',
                                              lead_source='50 Pound Challenge',
                                              telephone_number=saved_data.phone)
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', '50 Pound Challenge', 'Signup', referer)
            create_profile_output = create_stage_one_profile(request=request, email=saved_data.email,
                                                             source='50_pound_challenge', send_activation=False,
                                                             login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
                user.first_name = saved_data.name
                user.profile.telephone = saved_data.phone
                user.profile.save()
                user.save()
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='50_pound_challenge')

            text_email = get_template('fifty_pound_challenge/concierge_email_content.txt')
            c = Context({'name': saved_data.name,
                         'email': saved_data.email,
                         'phone': saved_data.phone,
                         'accounts': accounts})
            text_content = text_email.render(c)
            ConciergeUserNotes(user=user, note=text_content).save()
            send_email(
                subject='Fifty Pound Challenge Signup',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=('concierge@savingschampion.co.uk',),
            )
            from common.tasks import update_subscription_on_email_service
            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'Fifty Pound Challenge')
            return redirect('fifty_pound_challenge_thankyou')
    return render(request, 'fifty_pound_challenge/signup_form.html', {'form': form,
                                                                      'account_form': account_form,
                                                                      'account_form_helper': account_form_helper,
                                                                      'end_date': end_date})


def fifty_pound_challenge_thankyou(request):
    return render(request, 'fifty_pound_challenge/thankyou.html')


def product_questionaire_signup(request):
    form = ProductQuestionaireForm()
    if request.method == "POST":
        form = ProductQuestionaireForm(request.POST)
        if form.is_valid():
            saved_data = form.save()
            try:
                AdviserQueue(name=saved_data.name, email=saved_data.email,
                             telephone=saved_data.phone, source='Product Questionnaire').save()
                AdviserQueue.add_to_queue(email=saved_data.email,
                                          first_name=saved_data.name,
                                          last_name='.',
                                          lead_source='Product Questionnaire',
                                          telephone_number=saved_data.phone)
            except IntegrityError:
                if AdviserQueue.new_lead(saved_data.email):
                    adviser_queue = AdviserQueue.objects.get(email=saved_data.email)
                    if adviser_queue.status in [2, 8, 9, 10] and adviser_queue.adviser is not None:
                        adviser_queue.adviser = None
                    adviser_queue.interaction_started = datetime.datetime.now()
                    adviser_queue.save()
                    AdviserQueue.add_to_queue(email=saved_data.email,
                                              first_name=saved_data.name,
                                              last_name='.',
                                              lead_source='Product Questionnaire',
                                              telephone_number=saved_data.phone)
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'Product Questionaire', 'Signup', referer)
            create_profile_output = create_stage_one_profile(request=request, email=saved_data.email,
                                                             source='product_questionnaire', send_activation=False,
                                                             login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
                user.first_name = saved_data.name
                user.profile.telephone = saved_data.phone
                user.profile.save()
                user.save()
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='product_questionnaire')
            text_email = get_template('product_questionnaire/email_content.txt')
            c = Context({'name': saved_data.name})
            text_content = text_email.render(c)
            send_email(
                subject='Product Questionnaire',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=(saved_data.email,),
            )
            text_email = get_template('product_questionnaire/concierge_email_content.txt')
            c = Context({'name': saved_data.name,
                         'email': saved_data.email,
                         'phone': saved_data.phone,
                         'easy_access': saved_data.easy_access,
                         'notice_1_3': saved_data.notice_1_3,
                         'notice_3_6': saved_data.notice_3_6,
                         'fixed_rate_1': saved_data.fixed_rate_1,
                         'fixed_rate_2': saved_data.fixed_rate_2,
                         'funds': saved_data.funds,
                         })
            text_content = text_email.render(c)
            send_email(
                subject='Product Questionnaire Signup',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=('concierge@savingschampion.co.uk',),
            )

            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'Product Questionnaire')

            return redirect('product_questionnaire_thankyou')
    return render(request, 'product_questionnaire/signup_form.html', {'form': form})


def product_questionaire_thankyou(request):
    return render(request, 'product_questionnaire/thankyou.html')


def the_biggest_mistake_signup(request):
    form = TheBiggestMistakeForm()
    if request.method == "POST":
        form = TheBiggestMistakeForm(request.POST)
        if form.is_valid():
            saved_data = form.save()
            AdviserQueue.add_to_queue(email=saved_data.email,
                                      first_name=saved_data.name,
                                      last_name='.',
                                      lead_source='Seven Steps to Manage Cash in Excess of £100,000',
                                      telephone_number=saved_data.phone)

            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'Seven Steps to Manage Cash in Excess of £100,000', 'Signup', referer)
            create_profile_output = create_stage_one_profile(request=request, email=saved_data.email,
                                                             source='seven_steps_to_manage_cash_over_100000', send_activation=False,
                                                             login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
                user.first_name = saved_data.name
                user.profile.telephone = saved_data.phone
                user.profile.save()
                user.save()
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='the_value_of_advice')
            text_email = get_template('the_biggest_mistake/email_content.txt')
            c = Context({'name': saved_data.name})
            text_content = text_email.render(c)
            send_email(
                subject='Seven Steps to Manage Cash in Excess of £100,000',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=(saved_data.email,),
            )
            text_email = get_template('the_biggest_mistake/concierge_email_content.txt')
            c = Context({'name': saved_data.name,
                         'email': saved_data.email,
                         'phone': saved_data.phone})
            text_content = text_email.render(c)
            send_email(
                subject='Seven Steps to Manage Cash in Excess of £100,000',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=('concierge@savingschampion.co.uk',),
            )

            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'Biggest Mistakes Guide')

            return redirect('the_biggest_mistake_thankyou')
    return render(request, 'the_biggest_mistake/signup_form.html', {'form': form})


def the_biggest_mistake_thankyou(request):
    return render(request, 'the_biggest_mistake/thankyou.html')


def investec_baserate_plus_redirect(request):
    analytics('pageview', path=reverse('investec_baserate_plus_redirect'), title="Investec Product Page")
    return HttpResponseRedirect(
        'https://www.investec.co.uk/products-and-services/banking-services/personal-savings-accounts/base-rate-plus.html')


def investec_baserate_plus_signup(request):
    form = SavingsPriorityProductForm()
    if request.method == "POST":
        form = SavingsPriorityProductForm(request.POST)
        if form.is_valid():
            saved_data = form.save()
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'Savings Priority List', 'Investec_Signup', referer)
            create_profile_output = create_stage_one_profile(request=request, email=saved_data.email,
                                                             source='savings_priority_list_signup',
                                                             send_activation=False, login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
                user.first_name = saved_data.name
                user.profile.telephone = saved_data.phone
                user.profile.save()
                user.save()
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='savings_priority_list')
            text_email = get_template('savings_priority_list/email_content.txt')
            c = Context({'name': saved_data.name})
            text_content = text_email.render(c)
            send_email(
                subject='Savings Priority List',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=(saved_data.email,),
            )
            from common.tasks import update_subscription_on_email_service
            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'Investec Product')
            return investec_baserate_plus_thankyou(request)
    return render(request, 'investec_baserate_plus/signup_form.html', {'form': form})


def investec_baserate_plus_thankyou(request):
    return render(request, 'investec_baserate_plus/thankyou.html')


def product_faq(request, product_slug, context=None):
    if context is None:
        context = {}
    product_faq_object = ProductFAQ.objects.get(slug=product_slug)
    context['product_faq'] = product_faq_object
    context['product_questions'] = product_faq_object.productfaquestion_set.all()

    context['form'] = SavingsPriorityProductForm()
    if request.method == "POST":
        context['form'] = SavingsPriorityProductForm(request.POST)
        if context['form'].is_valid():
            saved_data = context['form'].save()
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'Savings Priority List', 'FAQ_{0}_Signup'.format(product_slug), referer)
            create_profile_output = create_stage_one_profile(request=request, email=saved_data.email,
                                                             source='savings_priority_list_signup',
                                                             send_activation=False, login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
                user.first_name = saved_data.name
                user.profile.telephone = saved_data.phone
                user.profile.save()
                user.save()
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='savings_priority_list')
            text_email = get_template('savings_priority_list/email_content.txt')
            c = Context({'name': saved_data.name})
            text_content = text_email.render(c)
            send_email(
                subject='Savings Priority List',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=(saved_data.email,),
            )

            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'Investec Product')

            return investec_baserate_plus_thankyou(request)

    return render(request, 'product_faq.html', context)


def fact_find_signup(request):
    form = FactFindForm()
    FactFindFormset = modelformset_factory(FactFindAccount, form=FactFindAccountForm, extra=1)
    account_form = FactFindFormset(queryset=FactFindAccount.objects.none(), prefix='accounts')
    account_form_helper = FactFindAccountFormHelper()
    end_date = datetime.datetime.now() + datetime.timedelta(weeks=2)
    if request.method == "POST":
        form = FactFindForm(request.POST)
        account_form = FactFindFormset(request.POST, prefix='accounts')
        if form.is_valid():
            saved_data = form.save()
            if account_form.is_valid():
                accounts = account_form.save(commit=False)
                for account in accounts:
                    account.challenge_signup = saved_data
                    if account.rate is not None and account.amount is not None:
                        account.save()
            else:
                accounts = []
            try:
                AdviserQueue(name=saved_data.name, email=saved_data.email,
                             telephone=saved_data.phone, source='50 Pound Challenge').save()

                AdviserQueue.add_to_queue(email=saved_data.email,
                                          first_name=saved_data.name,
                                          last_name='.',
                                          lead_source='50 Pound Challenge',
                                          telephone_number=saved_data.phone)
            except IntegrityError:
                if AdviserQueue.new_lead(saved_data.email):
                    adviser_queue = AdviserQueue.objects.get(email=saved_data.email)
                    if adviser_queue.status in [2, 8, 9, 10] and adviser_queue.adviser is not None:
                        adviser_queue.adviser = None
                    adviser_queue.interaction_started = datetime.datetime.now()
                    adviser_queue.save()
                    AdviserQueue.add_to_queue(email=saved_data.email,
                                              first_name=saved_data.name,
                                              last_name='.',
                                              lead_source='50 Pound Challenge',
                                              telephone_number=saved_data.phone)
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', '50 Pound Challenge', 'Signup', referer)
            create_profile_output = create_stage_one_profile(request=request, email=saved_data.email,
                                                             source='50_pound_challenge', send_activation=False,
                                                             login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
                user.first_name = saved_data.name
                user.profile.telephone = saved_data.phone
                user.profile.save()
                user.save()
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='50_pound_challenge')

            text_email = get_template('fact_find/concierge_email_content.txt')
            c = Context({'name': saved_data.name,
                         'email': saved_data.email,
                         'phone': saved_data.phone,
                         'accounts': accounts})
            text_content = text_email.render(c)
            ConciergeUserNotes(user=user, note=text_content).save()
            send_email(
                subject='50 Pound Challenge Signup',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=('concierge@savingschampion.co.uk',),
            )
            from common.tasks import update_subscription_on_email_service
            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'Fifty Pound Challenge')
            return redirect('fact_find_thankyou')
    return render(request, 'fact_find/signup_form.html', {'form': form,
                                                          'account_form': account_form,
                                                          'account_form_helper': account_form_helper,
                                                          'end_date': end_date})


def fact_find_thankyou(request):
    return render(request, 'fact_find/thankyou.html')


def pensioner_bonds(request):
    return redirect('view_article', post_slug='pensioner-bonds')


def pension_options_signup(request):
    form = PensionOptionsForm()
    if request.method == "POST":
        form = PensionOptionsForm(request.POST)
        if form.is_valid():
            saved_data = form.save()
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'Pension Options Guide', 'Signup', referer)
            user, user_created, record_stats = create_stage_one_profile(request=request, email=saved_data.email,
                                                                        source='pension_options_signup',
                                                                        send_activation=False,
                                                                        login_user=False)
            text_email = get_template('pension_options/email_content.txt')
            c = Context({'first_name': saved_data.first_name,
                         'last_name': saved_data.last_name
                         })
            text_content = text_email.render(c)
            # send_email(
            #     subject='Pension Options Guide',
            #     message=text_content,
            #     from_email='savings.champion@savingschampion.co.uk',
            #     recipient_list=(saved_data.email,),
            # )
            text_email = get_template('pension_options/concierge_email_content.txt')
            c = Context({'first_name': saved_data.first_name,
                         'last_name': saved_data.last_name,
                         'email': saved_data.email,
                         'postcode': saved_data.postcode,
                         'phone': saved_data.phone})
            text_content = text_email.render(c)
            send_email(
                subject='Pension Options Guide Signup',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=('ifa@savingschampion.co.uk',)  # 'leads@tpollp.com',
            )
            record_referral_signup(request=request, user=user, user_created=user_created, action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created, action='pension_options')
            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'Pension Options Guide')

            AdviserQueue.add_to_queue(email=saved_data.email,
                                      first_name=saved_data.first_name,
                                      last_name=saved_data.last_name,
                                      lead_source='pension_options',
                                      telephone_number=saved_data.phone)
            return redirect('pension_options_thankyou')
    return render(request, 'pension_options/signup_form.html', {'form': form})


def pension_options_thankyou(request):
    return render(request, 'pension_options/thank_you.html')


def static_redirect(request, file_location):
    resolved_url = static(file_location)
    return HttpResponseRedirect(resolved_url)


def mindful_money_healthcheck_signup(request):
    form = MindfulMoneyHealthcheckForm()
    if request.method == "POST":
        form = MindfulMoneyHealthcheckForm(request.POST)
        if form.is_valid():
            saved_data = form.save()
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'Mindful Money Healthcheck', 'Signup', referer)
            create_stage_one_profile(request=request, email=saved_data.email, source='mindful_money_healthcheck',
                                     send_activation=False, login_user=False)
            text_email = get_template('mindful_money_healthcheck/concierge_email_content.txt')
            c = Context({'first_name': saved_data.first_name,
                         'last_name': saved_data.last_name,
                         'email': saved_data.email,
                         'phone': saved_data.phone})
            text_content = text_email.render(c)
            send_email(
                subject='Mindful Money Healthcheck',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=('ifa@savingschampion.co.uk',)  # 'leads@tpollp.com',
            )

            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'Savings Healthcheck')
            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'Mindful Money')


            AdviserQueue.add_to_queue(email=saved_data.email,
                                      first_name=saved_data.first_name,
                                      last_name=saved_data.last_name,
                                      lead_source='mindful_money_healthcheck',
                                      telephone_number=saved_data.phone)
            return redirect('mindful_money_healthcheck_thankyou')
    return render(request, 'mindful_money_healthcheck/signup_form.html', {'form': form})


def mindful_money_healthcheck_thankyou(request):
    return render(request, 'mindful_money_healthcheck/thank_you.html')


def money_to_the_masses_signup(request):
    form = MoneyToTheMassesForm()
    if request.method == "POST":
        form = MoneyToTheMassesForm(request.POST)
        if form.is_valid():
            saved_data = form.save()
            try:
                AdviserQueue(name=saved_data.name, email=saved_data.email,
                             telephone=saved_data.phone, source='Money To The Masses').save()
                AdviserQueue.add_to_queue(email=saved_data.email,
                                          first_name=saved_data.name,
                                          last_name='.',
                                          lead_source='Money To The Masses',
                                          telephone_number=saved_data.phone)
            except IntegrityError:
                if AdviserQueue.new_lead(saved_data.email):
                    adviser_queue = AdviserQueue.objects.get(email=saved_data.email)
                    if adviser_queue.status in [2, 8, 9, 10] and adviser_queue.adviser is not None:
                        adviser_queue.adviser = None
                    adviser_queue.interaction_started = datetime.datetime.now()
                    adviser_queue.save()
                    AdviserQueue.add_to_queue(email=saved_data.email,
                                              first_name=saved_data.name,
                                              last_name='.',
                                              lead_source='Money To The Masses',
                                              telephone_number=saved_data.phone)
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'Money To The Masses', 'Signup', referer)
            create_profile_output = create_stage_one_profile(request=request, email=saved_data.email,
                                                             source='money_to_the_masses_signup', send_activation=False,
                                                             login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
                user.first_name = saved_data.name
                user.profile.telephone = saved_data.phone
                user.profile.save()
                user.save()
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='money_to_the_masses')
            text_email = get_template('money_to_the_masses/email_content.txt')
            c = Context({'name': saved_data.name})
            text_content = text_email.render(c)
            send_email(
                subject='Money To The Masses',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=(saved_data.email,),
            )
            text_email = get_template('money_to_the_masses/concierge_email_content.txt')
            c = Context({'name': saved_data.name,
                         'email': saved_data.email,
                         'phone': saved_data.phone})
            text_content = text_email.render(c)
            send_email(
                subject='Money To The Masses Signup',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=('concierge@savingschampion.co.uk',),
            )

            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'Seven Pitfalls Guide')
            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'Mindful Money')

            return redirect('money_to_the_masses_thankyou')
    return render(request, 'money_to_the_masses/signup_form.html', {'form': form})


def money_to_the_masses_thankyou(request):
    return render(request, 'money_to_the_masses/thankyou.html')


def challenger_banks_guide_signup(request):
    form = ChallengerBankGuideForm()
    if request.method == "POST":
        form = ChallengerBankGuideForm(request.POST)
        if form.is_valid():
            saved_data = form.save()
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'Challenger Bank Guide', 'Signup', referer)
            create_profile_output = create_stage_one_profile(request=request, email=saved_data.email,
                                                             source='challenger_banks_guide_signup',
                                                             send_activation=False, login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
                user.first_name = saved_data.name
                user.profile.save()
                user.save()
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='challenger_banks_guide')
            text_email = get_template('challenger_banks_guide/email_content.txt')
            c = Context({'name': saved_data.name})
            text_content = text_email.render(c)
            html_email = get_template('challenger_banks_guide/html_email_content.html')
            html_content = html_email.render(c)
            send_email(
                subject='Challenger Bank Guide',
                message=text_content,
                html_message=html_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=(saved_data.email,),
            )
            from common.tasks import update_subscription_on_email_service
            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'Challenger Bank Guide')
            return redirect('challenger_banks_guide_thankyou')
    return render(request, 'challenger_banks_guide/signup_form.html', {'form': form})


def challenger_banks_guide_thankyou(request):
    return render(request, 'challenger_banks_guide/thankyou.html')


def fb_iht_guide_signup(request, context=None):
    if context is None:
        context = {}
    form = FBIHTGuideForm()
    if request.method == "POST":
        form = FBIHTGuideForm(request.POST)
        if form.is_valid():
            saved_data = form.save()
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'IHT Guide', 'Signup', referer)
            create_profile_output = create_stage_one_profile(request=request, email=saved_data.email,
                                                             source='iht_guide_signup', send_activation=False,
                                                             login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
                user.first_name = saved_data.name
                user.profile.telephone = saved_data.phone
                user.profile.save()
                user.save()
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='iht_guide')
            text_email = get_template('fb_iht_guide/email_content.txt')
            html_email = get_template('fb_iht_guide/email_content.html')
            c = Context({'name': saved_data.name})
            text_content = text_email.render(c)
            html_content = html_email.render(c)
            send_email(
                subject='IHT Guide',
                message=text_content,
                html_message=html_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=(saved_data.email,),
            )
            text_email = get_template('fb_iht_guide/concierge_email_content.txt')
            c = Context({'name': saved_data.name,
                         'email': saved_data.email,
                         'phone': saved_data.phone})
            text_content = text_email.render(c)
            send_email(
                subject='IHT Guide Signup',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=('iht@savingschampion.co.uk',)  # 'leads@tpollp.com',
            )
            from common.tasks import update_subscription_on_email_service
            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'IHT Guide')
            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'Facebook')
            AdviserQueue.add_to_queue(email=saved_data.email,
                                      first_name=saved_data.name,
                                      last_name='.',
                                      lead_source='iht_guide',
                                      telephone_number=saved_data.phone)
            return redirect('fb_iht_guide_thankyou')
    context['form'] = form
    return render(request, 'fb_iht_guide/signup_form.html', context)


def fb_iht_guide_thankyou(request, context=None):
    return render(request, 'fb_iht_guide/thank_you.html', context)


def outbrain_iht_guide_signup(request, context=None):
    if context is None:
        context = {
            'image_static': 'img/ob_iht_guide/guide.jpg'
        }
    form = OBIHTGuideForm()
    if request.method == "POST":
        form = OBIHTGuideForm(request.POST)
        if form.is_valid():
            saved_data = form.save()
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'IHT Guide', 'Signup', referer)
            create_profile_output = create_stage_one_profile(request=request, email=saved_data.email,
                                                             source='iht_guide_signup', send_activation=False,
                                                             login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
                user.first_name = saved_data.name
                user.profile.telephone = saved_data.phone
                user.profile.save()
                user.save()
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='iht_guide')
            text_email = get_template('outbrain_iht_guide/email_content.txt')
            c = Context({'name': saved_data.name})
            text_content = text_email.render(c)
            send_email(
                subject='IHT Guide',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=(saved_data.email,),
            )
            text_email = get_template('outbrain_iht_guide/concierge_email_content.txt')
            c = Context({'name': saved_data.name,
                         'email': saved_data.email,
                         'phone': saved_data.phone})
            text_content = text_email.render(c)
            send_email(
                subject='IHT Guide Signup',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=('iht@savingschampion.co.uk',)  # 'leads@tpollp.com',
            )

            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'IHT Guide')
            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'Outbrain')

            AdviserQueue.add_to_queue(email=saved_data.email,
                                      first_name=saved_data.name,
                                      last_name='.',
                                      lead_source='iht_guide',
                                      telephone_number=saved_data.phone)
            return redirect('outbrain_iht_guide_thankyou')
    context['form'] = form
    return render(request, 'outbrain_iht_guide/signup_form.html', context)


def outbrain_iht_guide_thankyou(request, context=None):
    return render(request, 'outbrain_iht_guide/thank_you.html', context)


def iht_squeeze_page(request, context=None):
    if context is None:
        context = {}

    form = IHTSqueezePageForm()

    if request.method == "POST":
        form = IHTSqueezePageForm(request.POST)
        if form.is_valid():
            saved_data = form.save()
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'IHT Guide', 'Signup', referer)
            create_profile_output = create_stage_one_profile(request=request, email=saved_data.email,
                                                             source='iht_guide_signup', send_activation=False,
                                                             login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
                user.first_name = saved_data.name
                user.profile.telephone = saved_data.phone
                user.profile.save()
                user.save()
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='iht_guide')
            text_email = get_template('outbrain_iht_guide/email_content.txt')
            html_email = get_template('outbrain_iht_guide/email_content.html')
            c = Context({'name': saved_data.name})
            text_content = text_email.render(c)
            html_content = html_email.render(c)
            send_email(
                subject='IHT Guide',
                message=text_content,
                html_message=html_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=(saved_data.email,),
            )
            text_email = get_template('outbrain_iht_guide/concierge_email_content.txt')
            c = Context({'name': saved_data.name,
                         'email': saved_data.email,
                         'phone': saved_data.phone})
            text_content = text_email.render(c)
            send_email(
                subject='IHT Guide Signup',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=('iht@savingschampion.co.uk',)  # 'leads@tpollp.com',
            )

            update_subscription_on_email_service.delay(email=saved_data.email, interest_group=u'IHT Guide')

            AdviserQueue.add_to_queue(email=saved_data.email,
                                      first_name=saved_data.name,
                                      last_name='.',
                                      lead_source='iht_guide',
                                      telephone_number=saved_data.phone)
            return redirect('iht_squeeze_page_thankyou')

    context['form'] = form

    return render(request, 'iht_squeeze_page/form.html', context)


def iht_squeeze_page_thankyou(request, context=None):
    if context is None:
        context = {}

    return render(request, 'iht_squeeze_page/thank_you.html')


def psa_squeeze_page(request, context=None):
    if context is None:
        context = {}

    form = PSASqueezePageForm()

    if request.method == "POST":
        form = PSASqueezePageForm(request.POST)
        if form.is_valid():
            saved_data = form.save()
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'PSA Guide', 'Signup', referer)
            create_profile_output = create_stage_one_profile(request=request, email=saved_data.email,
                                                             source='psa_guide_signup',
                                                             send_activation=False,
                                                             login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
                user.first_name = ''
                user.save()
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='psa_guide')
            text_email = get_template('psa_squeeze_page/email_content.txt')
            html_email = get_template('psa_squeeze_page/email_content.html')
            c = Context({'email': saved_data.email})
            text_content = text_email.render(c)
            html_content = html_email.render(c)
            send_email(
                subject='PSA Guide',
                message=text_content,
                html_message=html_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=(saved_data.email,),
            )
            update_subscription_on_email_service.delay(saved_data.email, interest_group=u'PSA Guide')

            return redirect('psa_squeeze_page_thankyou')

    context['form'] = form

    return render(request, 'psa_squeeze_page/form.html', context)


def psa_squeeze_page_thankyou(request, context=None):
    if context is None:
        context = {}

    return render(request, 'psa_squeeze_page/thank_you.html')


def high_worth_squeeze_page(request, context=None):
    if context is None:
        context = {}

    form = HighWorthSqueezePageForm()

    if request.method == "POST":
        form = HighWorthSqueezePageForm(request.POST)
        if form.is_valid():
            saved_data = form.save()
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'High Worth Guide', 'Signup', referer)
            create_profile_output = create_stage_one_profile(request=request, email=saved_data.email,
                                                             source='high_worth_guide_signup', send_activation=False,
                                                             login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
                user.first_name = saved_data.name
                user.profile.telephone = saved_data.phone
                user.profile.save()
                user.save()
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='high_worth_guide')
            text_email = get_template('high_worth_squeeze_page/email_content.txt')
            html_email = get_template('high_worth_squeeze_page/email_content.html')
            c = Context({'name': saved_data.name})
            text_content = text_email.render(c)
            html_content = html_email.render(c)
            send_email(
                subject='2016 Financial Planning Tips for High Earners',
                message=text_content,
                html_message=html_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=(saved_data.email,),
            )
            text_email = get_template('high_worth_squeeze_page/concierge_email_content.txt')
            c = Context({'name': saved_data.name,
                         'email': saved_data.email,
                         'phone': saved_data.phone})
            text_content = text_email.render(c)
            send_email(
                subject='High Worth Guide Signup',
                message=text_content,
                from_email='savings.champion@savingschampion.co.uk',
                recipient_list=('concierge@savingschampion.co.uk',)  # 'leads@tpollp.com',
            )

            update_subscription_on_email_service.delay(email=saved_data.email, interest_group=u'High Worth Guide')

            AdviserQueue.add_to_queue(email=saved_data.email,
                                      first_name=saved_data.name,
                                      last_name='.',
                                      lead_source='high_worth_guide',
                                      telephone_number=saved_data.phone)
            return redirect('high_worth_squeeze_page_thankyou')

    context['form'] = form

    return render(request, 'high_worth_squeeze_page/form.html', context)


def high_worth_squeeze_page_thankyou(request, context=None):
    if context is None:
        context = {}

    return render(request, 'high_worth_squeeze_page/thank_you.html')