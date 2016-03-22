var docCookies = {
    getItem: function (sKey) {
        if (!sKey) {
            return null;
        }
        return decodeURIComponent(document.cookie.replace(new RegExp("(?:(?:^|.*;)\\s*" + encodeURIComponent(sKey).replace(/[\-\.\+\*]/g, "\\$&") + "\\s*\\=\\s*([^;]*).*$)|^.*$"), "$1")) || null;
    },
    setItem: function (sKey, sValue, vEnd, sPath, sDomain, bSecure) {
        if (!sKey || /^(?:expires|max\-age|path|domain|secure)$/i.test(sKey)) {
            return false;
        }
        var sExpires = "";
        if (vEnd) {
            switch (vEnd.constructor) {
                case Number:
                    sExpires = vEnd === Infinity ? "; expires=Fri, 31 Dec 9999 23:59:59 GMT" : "; max-age=" + vEnd;
                    break;
                case String:
                    sExpires = "; expires=" + vEnd;
                    break;
                case Date:
                    sExpires = "; expires=" + vEnd.toUTCString();
                    break;
            }
        }
        document.cookie = encodeURIComponent(sKey) + "=" + encodeURIComponent(sValue) + sExpires + (sDomain ? "; domain=" + sDomain : "") + (sPath ? "; path=" + sPath : "") + (bSecure ? "; secure" : "");
        return true;
    },
    removeItem: function (sKey, sPath, sDomain) {
        if (!this.hasItem(sKey)) {
            return false;
        }
        document.cookie = encodeURIComponent(sKey) + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT" + (sDomain ? "; domain=" + sDomain : "") + (sPath ? "; path=" + sPath : "");
        return true;
    },
    hasItem: function (sKey) {
        if (!sKey) {
            return false;
        }
        return (new RegExp("(?:^|;\\s*)" + encodeURIComponent(sKey).replace(/[\-\.\+\*]/g, "\\$&") + "\\s*\\=")).test(document.cookie);
    },
    keys: function () {
        var aKeys = document.cookie.replace(/((?:^|\s*;)[^\=]+)(?=;|$)|^\s*|\s*(?:\=[^;]*)?(?:\1|$)/g, "").split(/\s*(?:\=[^;]*)?;\s*/);
        for (var nLen = aKeys.length, nIdx = 0; nIdx < nLen; nIdx++) {
            aKeys[nIdx] = decodeURIComponent(aKeys[nIdx]);
        }
        return aKeys;
    }
};

var InitialScreen = React.createClass({
    displayName: "InitialScreen",
    clickHandler: function () {
        this.props.setParentNextStage();
    },
    render: function () {
        return (
            React.createElement("div", {className: "container-fluid"},
                React.createElement("div", {className: "row"},
                    React.createElement("div", {className: "col-md-12"},
                        React.createElement("p", null, "With our tool, you can find out:"),
                        React.createElement("ul", null,
                            React.createElement("li", null, "If you are eligible for THB protection"),
                            React.createElement("li", null, "If any of your deposits are at risk"),
                            React.createElement("li", null, "How to protect your funds"),
                            React.createElement("li", null, "How to get the best rates in the whole market"),
                            React.createElement("li", null, "How to be alerted for free when your protection expires")
                        ),
                        React.createElement("p", null, "Please Note: This tool is only for THBs – to check if your other savings are protected, call one of our savings advisers on 0800 321 3581 or check our ", React.createElement("a", {href: "https://www.savingschampion.co.uk/advice-guides/guides/fscs-licence-information/"}, "FSCS guide"), " for more information.")
                    )
                ),
                React.createElement("div", {className: "row"},
                    React.createElement("div", {className: "col-md-12"},
                        React.createElement("button", {
                            onClick: this.clickHandler,
                            className: "btn btn-primary pull-right"
                        }, "Begin")
                    )
                )
            )
        );
    }
});

var AdviserCallBack = React.createClass({
    displayName: "AdviserCallBack",
    getDefaultProps: function () {
        return {
            thb_eligible: false,
            user_products: [],
            source_token: '21c2b656e786cb1127136160bf0ffe976ad0dcc6'
        }
    },
    getInitialState: function () {
        return {
            name: '',
            email: '',
            phone_number: '',
            source: docCookies.getItem('referer'),
            done: false
        }
    },
    setReminder: function (event) {
        $.ajax({
            url: 'https://savingschampion.co.uk/api/v1/thb_tool_callback/',
            data: {
                'set_reminder': $(event.target).data('setReminder'),
                'book_callback': $(event.target).data('bookCallBack'),
                'name': this.state.name,
                'email': this.state.email,
                'phone_number': this.state.phone_number,
                'deposit_day': this.props.day,
                'deposit_month': this.props.month,
                'deposit_year': this.props.year,
                'source': this.state.source
            },
            headers: {
                'Authorization': 'Token ' + this.props.source_token
            },
            method: 'post',
            success: function () {
                this.setState({done: true})
            }.bind(this)
        })
    },
    mixins: [React.addons.LinkedStateMixin],
    render: function () {
        return (
            React.createElement("form", {className: "form-horizontal"},
                React.createElement("div", {className: "form-group"},
                    React.createElement("label", {className: "col-md-2 control-label"}, "Name: "),
                    React.createElement("div", {className: "col-md-10"},
                        React.createElement("input", {
                            className: "form-control",
                            type: "text",
                            id: "Name",
                            placeholder: "Full Name",
                            valueLink: this.linkState('name')
                        })
                    )
                ),
                React.createElement("div", {className: "form-group"},
                    React.createElement("label", {className: "col-md-2 control-label"}, "Email: "),
                    React.createElement("div", {className: "col-md-10"},
                        React.createElement("input", {
                            className: "form-control",
                            type: "text",
                            id: "Email",
                            placeholder: "Email Address",
                            valueLink: this.linkState('email')
                        })
                    )
                ),
                React.createElement("div", {className: "form-group"},
                    React.createElement("label", {className: "col-md-2 control-label"}, "Phone: "),
                    React.createElement("div", {className: "col-md-10"},
                        React.createElement("input", {
                            className: "form-control",
                            type: "text",
                            id: "Phone",
                            placeholder: "Phone Number",
                            valueLink: this.linkState('phone_number')
                        })
                    )
                ),
                React.createElement("div", {className: "form-controls"},
                    React.createElement("div", {className: "col-md-offset-2 col-md-10"},
                        React.createElement("div", {className: this.state.done ? "alert alert-success" : "hidden"},
                            React.createElement("p", null, "Thank you, your enquiry has been recorded.")
                        ),
                        React.createElement("input", {
                            type: "button",
                            className: "btn btn-primary",
                            value: this.props.thb_eligible ? "Set Reminder and Book Call Back" : "Book Call Back",
                            "data-set-reminder": this.props.thb_eligible ? "true" : "false",
                            "data-book-call-back": "true",
                            onClick: this.setReminder
                        }),
                        React.createElement("span", {className: this.props.thb_eligible ? "" : "hidden"}, " Or "),
                        React.createElement("input", {
                            type: "button",
                            className: this.props.thb_eligible ? "btn btn-default" : "hidden",
                            "data-set-reminder": "true",
                            "data-book-call-back": "",
                            value: "Set Reminder",
                            onClick: this.setReminder
                        })
                    )
                )
            )
        )
    }
})

var FirstScreen = React.createClass({
    displayName: "FirstScreen",
    getInitialState: function () {
        return {
            future_funds: 0,
            recent_funds: 0,
            eligible: 0
        }
    },
    handleRecentClick: function (event) {
        this.setState({
            recent_funds: Number(event.target.value),
            eligible: Number(event.target.value) + this.state.future_funds
        })
    },
    handleFutureClick: function (event) {
        this.setState({
            future_funds: Number(event.target.value),
            eligible: Number(event.target.value) + this.state.recent_funds
        })
    },
    handleReceiveMoneyClick: function () {
        $('#receive-money-modal').modal('show');
    },
    render: function () {
        return (
            React.createElement("div", {className: "container-fluid"},
                React.createElement("div", {className: "row"},
                    React.createElement("div", {className: "col-md-12"},
                        React.createElement("h1", null, "Check if you are eligible for Depositor Protection for Temporary High Balances (THBs)"),
                        React.createElement("hr", null)
                    )
                ),
                React.createElement("div", {className: "row"},
                    React.createElement("div", {className: "col-md-3"},
                        React.createElement("label", {htmlFor: "thb-tool-future-funds"}, "Are you waiting to receive money?"),
                        React.createElement("select", {
                                id: "thb-tool-future-funds",
                                className: "form-control",
                                onChange: this.handleFutureClick
                            },
                            React.createElement("option", {value: "0"}),
                            React.createElement("option", {value: "3"}, "Yes"),
                            React.createElement("option", {value: "1"}, "No")
                        )
                    ),
                    React.createElement("div", {className: "col-md-4"},
                        React.createElement("label", {htmlFor: "thb-tool-recent-funds"}, "Have you received money within the last 6 months? ", React.createElement("span", {
                            style: {cursor: 'pointer'},
                            className: "glyphicon glyphicon-question-sign",
                            onClick: this.handleReceiveMoneyClick
                        })),
                        React.createElement("select", {
                                id: "thb-tool-recent-funds",
                                className: "form-control",
                                onChange: this.handleRecentClick
                            },
                            React.createElement("option", {value: "0"}),
                            React.createElement("option", {value: "3"}, "Yes"),
                            React.createElement("option", {value: "1"}, "No")
                        )
                    ),
                    React.createElement("div", {className: "col-md-4 col-md-offset-1"},
                        React.createElement("button", {
                            className: "btn btn-primary",
                            disabled: this.state.eligible < 3,
                            onClick: this.props.setParentNextStage
                        }, "Check If My Money Qualifies")
                    )
                ),
                React.createElement("div", {className: "row"},
                    React.createElement("div", {className: this.state.eligible === 2 ? "col-md-12" : "hidden"},
                        React.createElement("hr", null),
                        React.createElement("div", {className: "alert alert-info"},
                            React.createElement("p", null, "Temporary High Balances (THBs) are only available for 6 months")
                        ),
                        React.createElement("h3", null, "You do not appear to be protected under the FSCS Temporary High Balances (THBs) Scheme"),
                        React.createElement("p", null, "Please call 0800 321 3581 to speak to a savings expert or you can request a free call back with the form below."),
                        React.createElement("p", null, "Our savings experts can:"),
                        React.createElement("ul", null,
                            React.createElement("li", null, "Explain what protection is available to you"),
                            React.createElement("li", null, "Identify how much of your money is currently at risk"),
                            React.createElement("li", null, "Help you to earn the best rates on your savings")
                        ),
                        React.createElement(AdviserCallBack, null)
                    )
                ),
                React.createElement("div", {className: "modal modal-small fade", id: "receive-money-modal"},
                    React.createElement("div", {className: "modal-dialog"},
                        React.createElement("div", {className: "modal-content"},
                            React.createElement("div", {className: "modal-header"},
                                React.createElement("h4", {className: "modal-title"}, "Time limit on Temporary High Balance Protection")
                            ),
                            React.createElement("div", {className: "modal-body"},
                                React.createElement("p", null, "Deposits over the normal FSCS limit are protected for six months from when the amount was first credited or from the moment a qualifying deposit became legally transferrable.")
                            ),
                            React.createElement("div", {className: "modal-footer"},
                                React.createElement("button", {
                                    type: "button",
                                    className: "btn btn-primary",
                                    "data-dismiss": "modal"
                                }, "Close")
                            )
                        )
                    )
                )
            )
        );
    }
});

var QualificationScreen = React.createClass({
    displayName: "QualificationScreen",
    incrementEvent: function () {
        var checkbox_count = $('form').find('input:checked').length
        this.getContinueButtonText(checkbox_count);
        $('#clarification-modal').modal('hide');
    },
    revertEvent: function (event) {
        var event_trigger = '#' + this.state.current_event_id;
        $(event_trigger).attr('checked', false);
        $('#clarification-modal').modal('hide');
    },
    getContinueButtonText: function (checkbox_count) {
        if (checkbox_count === 0) {
            this.setState({
                continue_button_text: 'None of these apply to me',
                event_count: checkbox_count,
                continue_button_class: 'btn btn-primary',
                user_done: false
            });
        } else if (checkbox_count > 0) {
            this.setState({
                continue_button_text: 'Continue',
                event_count: checkbox_count,
                continue_button_class: 'btn btn-primary',
                user_done: false
            });
        }
    },
    onChange: function (event) {
        if (event.target.checked) {
            var event_target_id = $(event.target).attr('id');
            var event_target_text = $(event.target).data('text');
            var event_target_addendum = $(event.target).data('addendum');
            this.setState({
                current_event_text: event_target_text,
                current_event_addendum: event_target_addendum,
                current_event_id: event_target_id,
                user_done: false
            });
            $('#clarification-modal').modal({'show': true, 'backdrop': 'static'});
        } else {
            var checkbox_count = $('form').find('input:checked').length
            this.getContinueButtonText(checkbox_count);
        }
    },
    getInitialState: function () {
        return {
            event_count: 0,
            current_event_text: '',
            current_event_id: '',
            continue_button_text: 'None of these apply to me',
            continue_button_class: 'btn btn-primary',
            user_done: false,
            current_event_addendum: ''
        };
    },
    handleContinueButton: function (event) {
        if (this.state.event_count === 1 && !this.state.unlimited) {
            this.props.setParentNextStage();
            this.props.setParentTHBEligable();
        } else {
            this.setState({
                user_done: true
            });
        }
    },
    onPIChange: function (event) {
        if (event.target.checked) {
            var event_target_id = $(event.target).attr('id');
            var event_target_text = $(event.target).data('text');
            var event_target_addendum = $(event.target).data('addendum');
            this.setState({
                current_event_text: event_target_text,
                current_event_addendum: event_target_addendum,
                current_event_id: event_target_id,
                unlimited: event.target.checked,
                user_done: false
            });
            $('#clarification-modal').modal({'show': true, 'backdrop': 'static'});
        } else {
            var checkbox_count = $('form').find('input:checked').length
            this.setState({
                unlimited: false
            })
            this.getContinueButtonText(checkbox_count);
        }
    },
    render: function () {
        return (
            React.createElement("div", {className: "container-fluid"},
                React.createElement("div", {className: "row"},
                    React.createElement("div", {className: "col-md-12"},
                        React.createElement("h1", null, "Where has your money come from?"),
                        React.createElement("hr", null)
                    )
                ),
                React.createElement("div", {className: "row"},
                    React.createElement("form", null,
                        React.createElement("div", {className: "col-md-4"},
                            React.createElement("div", {className: "form-group"},
                                React.createElement("label", {htmlFor: "buy-house"}, React.createElement("input", {
                                    className: "",
                                    id: "buy-house",
                                    "data-text": "Monies deposited in preparation for the purchase of a private residential property by the depositor",
                                    "data-addendum": "The private residential property must be your main or only residence",
                                    type: "checkbox",
                                    onChange: this.onChange
                                }), " Are you preparing to buy a house?")
                            ),
                            React.createElement("div", {className: "form-group"},
                                React.createElement("label", {htmlFor: "insurance-policy"}, React.createElement("input", {
                                    className: "",
                                    id: "insurance-policy",
                                    "data-text": "Benefits payable under an insurance policy",
                                    "data-addendum": "",
                                    type: "checkbox",
                                    onChange: this.onChange
                                }), " Has the money come from an insurance policy?")
                            ),
                            React.createElement("div", {className: "form-group"},
                                React.createElement("label", {htmlFor: "state-diabled"}, React.createElement("input", {
                                    className: "",
                                    id: "state-disabled",
                                    "data-text": "State benefits paid in respect of a disability or incapacity;",
                                    "data-addendum": "",
                                    type: "checkbox",
                                    onChange: this.onChange
                                }), " Have you received money from the govenment due to disability or incapacity?")
                            ),
                            React.createElement("div", {className: "form-group"},
                                React.createElement("label", {htmlFor: "injury-payout"}, React.createElement("input", {
                                    className: "",
                                    id: "injury-payout",
                                    "data-text": "Compensation for personal (including criminal) injury",
                                    "data-addendum": "",
                                    type: "checkbox",
                                    onChange: this.onPIChange
                                }), " Have you been compensated for an injury?")
                            ),
                            React.createElement("div", {className: "form-group"},
                                React.createElement("label", {htmlFor: "redundancy"}, React.createElement("input", {
                                    className: "",
                                    id: "redundancy",
                                    "data-text": "Redundancy (whether voluntary or compulsory)",
                                    "data-addendum": "",
                                    type: "checkbox",
                                    onChange: this.onChange
                                }), " Have you been made redundant?")
                            )
                        ),
                        React.createElement("div", {className: "col-md-4"},
                            React.createElement("div", {className: "form-group"},
                                React.createElement("label", {htmlFor: "sell-house"}, React.createElement("input", {
                                    className: "",
                                    id: "sell-house",
                                    "data-text": "Monies that represent the proceeds of sale of a private residential property",
                                    "data-addendum": "The private residential property must be your main or only residence",
                                    type: "checkbox",
                                    onChange: this.onChange
                                }), " Have you sold a house?")
                            ),
                            React.createElement("div", {className: "form-group"},
                                React.createElement("label", {htmlFor: "retired"}, React.createElement("input", {
                                    className: "",
                                    id: "retired",
                                    "data-text": "Benefits payable on retirement",
                                    "data-addendum": "",
                                    type: "checkbox",
                                    onChange: this.onChange
                                }), " Have you just retired?")
                            ),
                            React.createElement("div", {className: "form-group"},
                                React.createElement("label", {htmlFor: "divorce"}, React.createElement("input", {
                                    className: "",
                                    id: "divorce",
                                    "data-text": "Divorce or dissolution of a civil partnership",
                                    "data-addendum": "",
                                    type: "checkbox",
                                    onChange: this.onChange
                                }), " Is the money from a divorce or or dissolution of a civil partnership?")
                            ),
                            React.createElement("div", {className: "form-group"},
                                React.createElement("label", {htmlFor: "wrongful-conviction"}, React.createElement("input", {
                                    className: "",
                                    id: "wrongful-conviction",
                                    "data-text": "A claim for compensation for wrongful conviction",
                                    "data-addendum": "",
                                    type: "checkbox",
                                    onChange: this.onChange
                                }), " Have you been wrongfully convicted?")
                            ),
                            React.createElement("div", {className: "form-group"},
                                React.createElement("label", {htmlFor: "death"}, React.createElement("input", {
                                    className: "",
                                    id: "death",
                                    "data-text": "Benefits payable on death or a claim for compensation in respect of a person’s death",
                                    "data-addendum": "",
                                    type: "checkbox",
                                    onChange: this.onChange
                                }), " Is the money resulting from a death (excluding inheritance)?")
                            )
                        ),
                        React.createElement("div", {className: "col-md-4"},
                            React.createElement("div", {className: "form-group"},
                                React.createElement("label", {htmlFor: "equity-release"}, React.createElement("input", {
                                    className: "",
                                    id: "equity-release",
                                    "data-text": "Proceeds of an equity release in a private residential property",
                                    "data-addendum": "The private residential property must be your main or only residence",
                                    type: "checkbox",
                                    onChange: this.onChange
                                }), " Have you released some of the equity of your home?")
                            ),
                            React.createElement("div", {className: "form-group"},
                                React.createElement("label", {htmlFor: "marriage"}, React.createElement("input", {
                                    className: "",
                                    id: "marriage",
                                    "data-text": "Marriage or civil partnership",
                                    "data-addendum": "",
                                    type: "checkbox",
                                    onChange: this.onChange
                                }), " Has the money been received due to a marriage or civil partnership?")
                            ),
                            React.createElement("div", {className: "form-group"},
                                React.createElement("label", {htmlFor: "unfair-dismissal"}, React.createElement("input", {
                                    className: "",
                                    id: "unfair-dismissal",
                                    "data-text": "A claim for compensation for unfair dismissal",
                                    "data-addendum": "",
                                    type: "checkbox",
                                    onChange: this.onChange
                                }), " Have you claimed for unfair dismissal?")
                            ),
                            React.createElement("div", {className: "form-group"},
                                React.createElement("label", {htmlFor: "inheritance"}, React.createElement("input", {
                                    className: "",
                                    id: "inheritance",
                                    "data-text": "A legacy or other distribution from the estate of a deceased person; or it is held in an account on behalf of the personal representative of a deceased person for the purpose of realising and administering the deceased’s estate.",
                                    "data-addendum": "",
                                    type: "checkbox",
                                    onChange: this.onChange
                                }), " Is the money part of an inheritance?")
                            )
                        )
                    )
                ),

                React.createElement("div", {className: "row"},
                    React.createElement("input", {
                        className: this.state.continue_button_class,
                        type: "button",
                        value: this.state.continue_button_text,
                        onClick: this.handleContinueButton
                    }),

                    React.createElement("div", {className: (this.state.user_done && this.state.event_count > 1 && !this.state.unlimited) ? "" : "hidden"},
                        React.createElement("hr", null),
                        React.createElement("p", null, "You have selected more than one life event. THB protection can be complex if you have had multiple life events."),
                        React.createElement("p", null, "We strongly recommend you seek advice."),
                        React.createElement("p", null, "Please call 0800 321 3581 to speak to a savings expert or you can request a free call back with the form below."),
                        React.createElement("p", null, "Our savings experts can:"),
                        React.createElement("ul", null,
                            React.createElement("li", null, "Explain what protection is available to you"),
                            React.createElement("li", null, "Identify how much of your money is currently at risk"),
                            React.createElement("li", null, "Help you to earn the best rates on your savings")
                        ),
                        React.createElement(AdviserCallBack, null)
                    ),
                    React.createElement("div", {className: (this.state.user_done && this.state.event_count === 0) ? "" : "hidden"},
                        React.createElement("hr", null),
                        React.createElement("div", {className: "alert alert-info"},
                            React.createElement("p", null, "Temporary High Balances (THBs) are only available when you have experienced a life event.")
                        ),
                        React.createElement("h3", null, "You do not appear to be protected under the FSCS Temporary High Balances (THBs) Scheme"),
                        React.createElement("p", null, "However, your money may still be protected under other FSCS schemes, please give Savings Champion a call on 0800 321 3581 or you can request a free callback with the form below"),
                        React.createElement(AdviserCallBack, null)
                    ),
                    React.createElement("div", {className: (this.state.unlimited && this.state.user_done) ? "" : "hidden"},
                        React.createElement("hr", null),
                        React.createElement("h3", null, "THB Protection for personal injury compensation claims"),
                        React.createElement("p", null, "Temporary High Balance Protection for a compensation claim for personal injury is unlimited for 6 months."),
                        React.createElement("p", null, "To be alerted when your protection expires and to get the best savings rates in the whole market, you can request a free callback with the form below or call us on 0800 321 3581"),
                        React.createElement(AdviserCallBack, null)
                    )
                ),

                React.createElement("div", {className: "modal fade", id: "clarification-modal"},
                    React.createElement("div", {className: "modal-dialog"},
                        React.createElement("div", {className: "modal-content"},
                            React.createElement("div", {className: "modal-header"},
                                React.createElement("h4", {className: "modal-title"}, "The Official Eligibility Statement from the FSCS")
                            ),
                            React.createElement("div", {className: "modal-body"},
                                React.createElement("h5", null, "Just to double check, the following statement is what the FSCS will judge your claim against."),
                                React.createElement("p", null, "\"", this.state.current_event_text, "\""),
                                React.createElement("p", null, this.state.current_event_addendum),
                                React.createElement("p", null, React.createElement("b", null, "Are you still sure this applies to you?")),
                                React.createElement("p", null, "If you are unsure, call 0800 321 3581 to speak to a savings expert.")
                            ),
                            React.createElement("div", {className: "modal-footer"},
                                React.createElement("button", {
                                    type: "button",
                                    className: "btn btn-default",
                                    onClick: this.revertEvent
                                }, "I am not eligible"),
                                React.createElement("button", {
                                    type: "button",
                                    className: "btn btn-primary",
                                    onClick: this.incrementEvent
                                }, "I am eligible")
                            )
                        )
                    )
                )
            )
        )
    }
});

var functionally_remove_item_from_array_by_key = function (array, key) {
    var new_array = []
    if (array.length > 0) {
        new_array = array.filter(
            function (element, index, array) {
                if (element.hasOwnProperty('key')) {
                    if (element.key == key) {  // implicit as react alters key on ReactElement to a string value...
                        return false;
                    }
                    return true;
                }
                return true;
            }
        )
    }
    return new_array;
}

var numberWithCommas = function (x) {
    var parts = x.toString().split(".");
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return parts.join(".");
}

var getRandomArbitrary = function (min, max) {
    return Math.random() * (max - min) + min;
}

var ProviderLineItem = React.createClass({
    displayName: "ProviderLineItem",
    getInitialState: function () {
        var parent_providers = this.props.providers
        var providers = parent_providers.map(
            function (provider) {
                return (
                    React.createElement("option", {key: provider.id, value: provider.id}, provider.title)
                );
            }
        );
        return {
            providers: providers,
            balance: ""
        };
    },
    getDefaultProps: function () {
        return {
            enabled: true,
            key_id: 1,
        }
    },
    deleteLineItem: function () {
        this.props.deleteLineItem(this.props.key_id);
    },
    changeBalance: function (event) {
        var entered_balance = $(event.target).val().replace(/[^\d.]/g, '');
        var new_balance = numberWithCommas(entered_balance);
        this.setState({
            balance: new_balance
        })
        this.props.rowAttribchange(event)
    },
    render: function () {
        return (
            React.createElement("div", {className: "form-row"},
                React.createElement("div", {className: "form-group"},
                    React.createElement("label", {htmlFor: "provider" + this.props.key_id}, "Bank/Building Society"),
                    React.createElement("select", {
                            disabled: !this.props.enabled,
                            className: "form-control",
                            id: "provider" + this.props.key_id,
                            "data-key": this.props.key_id,
                            "data-row-attribute": "provider",
                            onChange: this.props.rowAttribchange
                        },
                        this.state.providers
                    )
                ),
                React.createElement("div", {className: "form-group"},
                    React.createElement("label", {htmlFor: "balance" + this.props.key_id}, "Total Balance"),
                    React.createElement("input", {
                        type: "text",
                        disabled: !this.props.enabled,
                        className: "form-control",
                        "data-key": this.props.key_id,
                        id: "balance" + this.props.key_id,
                        "data-row-attribute": "balance",
                        placeholder: "How much money do you have with this provider?",
                        value: this.state.balance,
                        onChange: this.changeBalance
                    })
                ),
                React.createElement("button", {
                    type: "button",
                    className: "btn btn-danger",
                    onClick: this.deleteLineItem
                }, "Remove"),
                React.createElement("hr", null)
            )
        )
    }
})

var AccountBalances = React.createClass({
    displayName: "AccountBalances",
    getDefaultProps: function () {
        return {
            thb_eligible: false,
            source: 'https://savingschampion.co.uk/api/v1/providers/?format=json&page_size=10000',
            source_token: '21c2b656e786cb1127136160bf0ffe976ad0dcc6',
            source_page_size: 1000
        };
    },
    getInitialState: function () {
        return {
            number_of_line_items: 1,
            used_key_ids: [1],
            line_items: [],
            providers_list: [
                {
                    id: 0,
                    title: 'Loading latest provider list...'
                },
            ],
            providers_list_loaded: false,
        }
    },
    componentDidMount: function () {
        $.ajax({
            url: 'https://savingschampion.co.uk/api/v1/providers/?format=json&page_size=' + this.props.source_page_size,
            headers: {
                'Authorization': 'Token ' + this.props.source_token
            },
            dataType: 'json',
            success: function (result) {
                var results = result['results']
                if (this.isMounted()) {
                    this.setState({
                        providers_list: results,
                        providers_list_loaded: true
                    });
                    this.addLineItem();
                }
            }.bind(this)
        });
    },
    deleteThisLineItem: function (key) {
        var new_number_of_items = (key - 1);
        var updated_line_items = functionally_remove_item_from_array_by_key(this.state.line_items, key);
        var updated_used_keys = this.state.used_key_ids.filter(
            function (element, index, array) {
                return !(element === key)
            }
        )
        this.setState({
            number_of_line_items: new_number_of_items,
            used_key_ids: updated_used_keys,
            line_items: updated_line_items
        });
    },
    getUnusedProductLineId: function () {
        var n = 0
        var comparison = false
        while (n < 1000) {
            n = n + 1
            comparison = this.state.used_key_ids.indexOf(n) > -1
            if (!comparison) {
                return n
            }
        }
        console.log('User has used over 1000 providers? really? Fall back to chance I guess?')
        return getRandomArbitrary(1000, 10000)
    },
    addLineItem: function () {
        var new_number_of_items = this.state.number_of_line_items + 1
        var key = this.getUnusedProductLineId()
        var updated_used_keys = this.state.used_key_ids.concat([key])
        var line_items = this.state.line_items.concat([
            React.createElement(ProviderLineItem, {
                key: new_number_of_items,
                deleteLineItem: this.deleteThisLineItem,
                key_id: new_number_of_items,
                providers: this.state.providers_list,
                rowAttribchange: this.props.saveChangedValues
            })
        ])
        this.setState({
            line_items: line_items,
            used_key_ids: updated_used_keys,
            number_of_line_items: new_number_of_items
        })
    },
    notFSCS: function (event) {
        $('#not-fscs-modal').modal('show');
    },
    overSixMonths: function () {
        var deposit_moment = moment({
            year: this.props.year,
            month: this.props.month,
            day: this.props.day,
        })
        var today_moment = moment()
        return (deposit_moment < today_moment.subtract(6, 'months'))
    },
    render: function () {
        var today = new Date();
        var year = [(today.getFullYear() - 1), today.getFullYear(), (today.getFullYear() + 1), (today.getFullYear() + 2)]
        var month = Array.apply(null, Array(12)).map(function (_, i) {
            return i;
        });
        var day = Array.apply(null, Array(31)).map(function (_, i) {
            return i;
        });
        return (
            React.createElement("div", {className: "container-fluid"},
                React.createElement("div", {className: "row"},
                    React.createElement("div", {className: "col-md-12"},
                        React.createElement("h1", null, "Check if your deposits are at risk")
                    )
                ),
                React.createElement("div", {className: this.props.thb_eligible ? "row" : "hidden"},
                    React.createElement("div", {className: "col-md-12"},
                        React.createElement("hr", null),
                        React.createElement("h3", null, "When did/will you receive the money?"),
                        React.createElement("form", {className: "form-inline"},
                            React.createElement("div", {className: "form-group"},
                                React.createElement("label", null, "Day: ", React.createElement("select", {
                                        className: "form-control",
                                        defaultValue: today.getDate(),
                                        onChange: this.props.saveChangedDay
                                    },

                                    day.map(function (value) {
                                        return React.createElement("option", {value: value + 1}, value + 1)
                                    })
                                ))
                            ),
                            React.createElement("div", {className: "form-group"},
                                React.createElement("label", null, "Month: ", React.createElement("select", {
                                        className: "form-control",
                                        defaultValue: today.getMonth() + 1,
                                        onChange: this.props.saveChangedMonth
                                    },

                                    month.map(function (value) {
                                        return React.createElement("option", {value: value + 1}, value + 1)
                                    })
                                ))
                            ),
                            React.createElement("div", {className: "form-group"},
                                React.createElement("label", null, "Year: ", React.createElement("select", {
                                        className: "form-control",
                                        defaultValue: today.getFullYear(),
                                        onChange: this.props.saveChangedYear
                                    },

                                    year.map(function (value) {
                                        return React.createElement("option", {value: value}, value)
                                    })
                                ))
                            )
                        )
                    )
                ),
                React.createElement("div", {className: this.overSixMonths() ? "hidden" : "row"},
                    React.createElement("div", {className: "col-md-12"},
                        React.createElement("hr", null),
                        React.createElement("h3", null, "Where is your money currently/due to be deposited?"),
                        this.state.line_items
                    )
                ),
                React.createElement("div", {className: this.overSixMonths() ? "hidden" : "row"},
                    React.createElement("div", {className: "col-md-2"},
                        React.createElement("input", {
                            type: "button",
                            className: this.state.providers_list_loaded ? "hidden" : "btn btn-default",
                            disabled: true,
                            value: "Please Wait, Loading List Of Providers"
                        }),
                        React.createElement("input", {
                            type: "button",
                            className: this.state.providers_list_loaded ? "btn btn-success" : "hidden",
                            onClick: this.addLineItem,
                            value: this.state.number_of_line_items === 1 ? "Add A Deposit" : "Add Another"
                        })
                    ),
                    React.createElement("div", {className: "col-md-4"},
                        React.createElement("input", {
                            className: "btn btn-info",
                            value: "Why is my bank or building society not in the list?",
                            type: "button",
                            onClick: this.notFSCS
                        })
                    ),
                    React.createElement("div", {className: "col-md-4 col-md-offset-2"},
                        React.createElement("input", {
                            type: "button",
                            className: "btn btn-primary pull-right",
                            disabled: this.state.number_of_line_items === 1,
                            onClick: this.props.setParentNextStage,
                            value: "Show My Results"
                        })
                    )
                ),
                React.createElement("div", {className: "row"},
                    React.createElement("div", {className: this.overSixMonths() ? "col-md-12" : "hidden"},
                        React.createElement("hr", null),
                        React.createElement("div", {className: "alert alert-info"},
                            React.createElement("p", null, "Temporary High Balances (THBs) are only available for 6 months")
                        ),
                        React.createElement("h3", null, "You do not appear to be protected under the FSCS Temporary High Balances (THBs) Scheme"),
                        React.createElement("p", null, "Please call 0800 321 3581 to speak to a savings expert or you can request a free call back with the form below."),
                        React.createElement("p", null, "Our savings experts can:"),
                        React.createElement("ul", null,
                            React.createElement("li", null, "Explain what protection is available to you"),
                            React.createElement("li", null, "Identify how much of your money is currently at risk"),
                            React.createElement("li", null, "Help you to earn the best rates on your savings")
                        ),
                        React.createElement(AdviserCallBack, null)
                    )
                ),
                React.createElement("div", {className: "modal fade", id: "not-fscs-modal"},
                    React.createElement("div", {className: "modal-dialog"},
                        React.createElement("div", {className: "modal-content"},
                            React.createElement("div", {className: "modal-header"},
                                React.createElement("button", {
                                    type: "button",
                                    className: "close",
                                    "data-dismiss": "modal",
                                    "aria-label": "Close"
                                }, React.createElement("span", {"aria-hidden": "true"}, "×")),
                                React.createElement("h4", {className: "modal-title"}, "Why is my bank or building society not in the list?")
                            ),
                            React.createElement("div", {className: "modal-body"},
                                React.createElement("p", null, "The FSCS protects savings of up to £85,000 per person per banking licence (reducing to £75,000 from 1 January 2016) with all banks, building societies and credit unions that are authorised by the Prudential Regulation Authority (PRA) and the Financial Conduct Authority (FCA)."),

                                React.createElement("p", null, "Your savings might not be protected by the FSCS if you can't find your bank, building society or credit union on our tool. To check if your provider is authorised call 0800 321 3581 and speak to a savings expert."),
                                React.createElement("p", null, "Alternatively you can use the ", React.createElement("a", {
                                    target: "_blank",
                                    href: "http://www.fsa.gov.uk/register/firmSearchForm.do"
                                }, "FCA’s Firm Check Service"))
                            )
                        )
                    )
                )
            )
        );
    }
});


var ProviderResult = React.createClass({
    displayName: "ProviderResult",
    getDefaultProps: function () {
        return {
            provider: 'Test Provider',
            balance: 1000,
            protected_balance: 0,
            fscs_conflict: false,
            fscs_conflict_providers: []
        }
    },
    render: function () {
        var conflicting_providers = this.props.fscs_conflict_providers
        return (
            React.createElement("div", {className: "container-fluid"},
                React.createElement("div", {className: "row"},
                    React.createElement("div", {className: "col-md-6"},
                        React.createElement("p", null, this.props.provider, " - "),
                        React.createElement("p", null, "£", numberWithCommas(this.props.balance))
                    ),
                    React.createElement("div", {className: "col-md-6"},
                        React.createElement("p", {className: this.props.fscs_conflict ? "hidden" : ""}, "This provider does not share an FSCS licence and gets the full £1m protection"),
                        React.createElement("p", {className: this.props.fscs_conflict ? "" : "hidden"}, "This provider shares an FSCS licence with the following providers you’ve told us you have funds with:"),
                        React.createElement("ul", {className: this.props.fscs_conflict ? "" : "hidden"},

                            conflicting_providers.map(
                                function (fscs_conflict_provider) {
                                    return React.createElement("li", {key: fscs_conflict_provider}, fscs_conflict_provider)
                                }
                            )
                        ),
                        React.createElement("p", {className: this.props.fscs_conflict ? "hidden" : ""}, "Only £1m total is protected for this provider"),
                        React.createElement("p", {className: this.props.fscs_conflict ? "" : "hidden"}, "Only £1m in total is protected across all of these providers")
                    )
                )
            )
        )
    }
})

var ResultsScreen = React.createClass({
    displayName: "ResultsScreen",
    getDefaultProps: function () {
        return {
            user_providers: {},
            source_page_size: 1000,
            source_token: '21c2b656e786cb1127136160bf0ffe976ad0dcc6'
        }
    },
    getInitialState: function () {
        return {
            providers_list: [],
            easier_user_providers: {},
            results: [],
            risky_money: 0,
            temporary_protection: 0,
            continue: false,
            best_rate: false,
            full_protection: false,
            alert_me: false
        }
    },
    componentDidMount: function () {
        $.ajax({
            url: 'https://savingschampion.co.uk/api/v1/providers/?format=json&page_size=' + this.props.source_page_size,
            headers: {
                'Authorization': 'Token ' + this.props.source_token
            },
            dataType: 'json',
            success: function (result) {
                var results = result['results']
                if (this.isMounted()) {
                    this.setState({
                        providers_list: results
                    });
                    this.calculateResults()
                }
            }.bind(this)
        });
    },
    calculateResults: function () {
        var required_providers = []
        var user_providers = this.props.user_providers
        var providers_list = this.state.providers_list
        var easier_providers = {}
        var easier_user_providers = {}
        var results = []
        var total_balance = 0
        // this.props.user_providers.forEach(
        //   function(value, key, object) {
        //     required_providers = required_providers.concat([value['provider']])
        //   }
        // );


        for (var prop in user_providers) {
            if (user_providers.hasOwnProperty(prop)) {
                console.log("up." + prop + " = " + user_providers[prop]);
                required_providers = required_providers.concat([user_providers[prop]['provider']])
                easier_user_providers[user_providers[prop]['provider']] = {
                    'balance': user_providers[prop]['balance']
                }
                total_balance = total_balance + Number(user_providers[prop]['balance'])
            }
        }

        providers_list.forEach(
            function (value, key, array) {
                easier_providers[value.id] = value
            }
        )


        var provider
        var risky_money = 0

        providers_list.forEach(
            function (value, key, array) {
                provider = value;
                if (required_providers.indexOf(String(provider.id)) > -1) {

                    easier_user_providers[provider.id]['object'] = provider
                    easier_user_providers[provider.id]['fscs_clash'] = false;
                    easier_user_providers[provider.id]['fscs_shared_provider_names'] = []

                    var combined_fscs_balance = Number(easier_user_providers[provider.id]['balance']);

                    if (provider['get_shared_licence_providers'].length > 1) {
                        provider['get_shared_licence_providers'].forEach(
                            function (value, key, array) {
                                if (value !== provider.id) {
                                    if (required_providers.indexOf(String(value)) > -1) {
                                        combined_fscs_balance = combined_fscs_balance + Number(easier_user_providers[value]['balance']);
                                        easier_user_providers[provider.id]['fscs_shared_provider_names'].push(easier_providers[value]['title'])
                                        easier_user_providers[provider.id]['fscs_clash'] = true;
                                    }
                                }
                            }.bind(this)
                        )
                    }


                    // If there is an FSCS conflict, use the combined balance to check protection level.
                    if (easier_user_providers[provider.id]['fscs_clash'] && 1000000 >= combined_fscs_balance) {
                        easier_user_providers[provider.id]['protected_balance'] = true
                    } else if (!easier_user_providers[provider.id]['fscs_clash'] && 1000000 >= easier_user_providers[provider.id]['balance']) {
                        // all money is protected
                        easier_user_providers[provider.id]['protected_balance'] = true
                    } else {
                        // money isn't protected
                        if (easier_user_providers[provider.id]['fscs_clash']) {
                            risky_money = risky_money + ((combined_fscs_balance - 1000000) / (easier_user_providers[provider.id]['fscs_shared_provider_names'].length + 1 ))
                        } else {
                            risky_money = risky_money + (easier_user_providers[provider.id]['balance'] - 1000000)
                        }
                        easier_user_providers[provider.id]['protected_balance'] = false
                    }


                }
            }.bind(this)
        )

        for (var prop in easier_user_providers) {
            if (easier_user_providers.hasOwnProperty(prop)) {
                var value = easier_user_providers[prop]
                results = results.concat([

                    React.createElement(ProviderResult, {
                        provider: value.object.title,
                        balance: value.balance,
                        fscs_conflict: value.fscs_clash,
                        fscs_conflict_providers: value.fscs_shared_provider_names,
                        thb_eligible: this.props.thb_eligible,
                        protected_balance: value.protected_balance
                    }),
                    React.createElement("hr", null)
                ])
            }
        }


        this.setState({
            results: results,
            risky_money: risky_money,
            temporary_protection: total_balance - risky_money
        })

        console.log(required_providers);
    },
    getSixMonthsTime: function () {
        var day = this.props.day
        var month = this.props.month
        var year = this.props.year
        var deposit_date = moment({
            year: year,
            month: month,
            day: day
        })
        return deposit_date.add(6, 'months').format('D/M/YYYY');
    },
    continueForm: function () {
        this.setState({
            continue: true
        })
    },
    mixins: [React.addons.LinkedStateMixin],
    render: function () {
        return (
            React.createElement("div", {className: "container-fluid"},
                React.createElement("div", {className: "row"},
                    React.createElement("div", {className: "col-md-12"},
                        React.createElement("h1", null, "Results")
                    )
                ),
                React.createElement("div", {className: "row"},
                    React.createElement("div", {className: "col-md-6"},
                        React.createElement("h3", null, "Based upon the information you have provided:"),
                        React.createElement("div", {className: "alert alert-danger"},
                            React.createElement("p", null, "£", numberWithCommas(this.state.risky_money), " of your money is at risk now."),
                            React.createElement("p", {className: this.props.thb_eligible ? "" : "hidden"}, "£", numberWithCommas(this.state.temporary_protection), " of your money is temporarily protected until ", this.getSixMonthsTime())
                        ),
                        React.createElement("hr", null),
                        this.state.results
                    ),
                    React.createElement("div", {className: "col-md-6"},
                        React.createElement("h1", null, "Action Required:"),

                        React.createElement("label", {className: this.state.temporary_protection > 0 ? "" : "hidden"}, React.createElement("input", {
                            type: "checkbox",
                            checkedLink: this.linkState('full_protection')
                        }), " Get my deposits fully protected"),
                        React.createElement("label", null, React.createElement("input", {
                            type: "checkbox",
                            checkedLink: this.linkState('best_rate')
                        }), " Get the best savings rates in the whole market"),
                        React.createElement("label", null, React.createElement("input", {
                            type: "checkbox",
                            checkedLink: this.linkState('alert_me')
                        }), " Alert me 2 weeks before my protection expires"),

                        React.createElement("input", {
                            type: "button",
                            className: "btn btn-primary",
                            value: "Continue",
                            disabled: !(this.state.best_rate || this.state.full_protection || this.state.alert_me),
                            onClick: this.continueForm
                        }),
                        React.createElement("div", {className: this.state.continue && (this.state.best_rate || this.state.full_protection || this.state.alert_me) ? "" : "hidden"},
                            React.createElement("hr", null),
                            React.createElement("h2", null, "Please Enter Your Details"),
                            React.createElement("p", {className: this.state.best_rate || this.state.full_protection ? "" : "hidden"}, "To ensure ", React.createElement("span", {className: this.state.best_rate ? "" : "hidden"}, "you get the best savings rates"), " ", React.createElement("span", {className: this.state.best_rate && this.state.full_protection ? "" : "hidden"}, "and"), " ", React.createElement("span", {className: this.state.full_protection ? "" : "hidden"}, "your deposits are fully protected"), ", please book a call back using the form below."),
                            React.createElement("p", {className: this.state.alert_me ? "" : "hidden"}, "We will ", React.createElement("span", {className: this.state.best_rate || this.state.full_protection ? "" : "hidden"}, "also"), " alert you 2 weeks before your existing protection expires"),
                            React.createElement(AdviserCallBack, {
                                thb_eligible: this.props.thb_eligible && this.state.alert_me,
                                day: this.props.day,
                                month: this.props.month,
                                year: this.props.year
                            }),
                            React.createElement("p", null, "Alternatively call 0800 321 3581 to speak to a savings expert")
                        )
                    )
                )
            )
        )
    }
})

var FSCSTool = React.createClass({
    displayName: "FSCSTool",
    getInitialState: function () {
        var today = new Date();
        return {
            stage: 1,
            thb_eligible: false,
            user_providers: {},
            day: today.getDate(),
            month: (today.getMonth() + 1 ),
            year: today.getFullYear(),
            unlimited: false
        }
    },
    nextStage: function () {
        var newStage = 1;
        if (this.state.stage < 5) {
            newStage = this.state.stage + 1;
        }
        if (newStage === 4) {
            this.setState({
                user_providers: {}
            })
        }
        this.setState({'stage': newStage});
    },
    previousStage: function () {
        var newStage = 1;
        if (this.state.stage > 1) {
            newStage = this.state.stage - 1;
        }
        if (newStage === 4) {
            this.setState({
                user_providers: {}
            })
        }
        this.setState({'stage': newStage});
    },
    setTHBEligable: function () {
        this.setState({
            thb_eligible: true
        });
    },
    setTHBNotEligable: function () {
        this.setState({
            thb_eligible: false
        });
    },
    saveChangedValues: function (event) {
        var row_key = $(event.target).data('key');
        var changed_attribute = $(event.target).data('rowAttribute');
        var value = $(event.target).val();
        var changed_state = this.state.user_providers
        if (!(row_key in changed_state)) {
            changed_state[row_key] = {};
        }
        changed_state[row_key][changed_attribute] = value.replace(/[^\d.]/g, '')
        this.setState({
            user_providers: changed_state
        })
    },
    depositDayChange: function (event) {
        this.setState({day: Number(event.target.value)})
    },
    depositMonthChange: function (event) {
        this.setState({month: Number(event.target.value)})
    },
    depositYearChange: function (event) {
        this.setState({year: Number(event.target.value)})
    },
    setUnlimited: function (meh) {
        this.setState({
            unlimited: meh
        })
    },
    render: function () {
        var active_component;
        if (this.state.stage === 1) {
            active_component = React.createElement(InitialScreen, {
                setParentNextStage: this.nextStage,
                setParentPrevStage: this.previousStage
            });
        } else if (this.state.stage === 2) {
            active_component = React.createElement(FirstScreen, {
                setParentNextStage: this.nextStage,
                setParentPrevStage: this.previousStage
            });
        } else if (this.state.stage === 3) {
            active_component = React.createElement(QualificationScreen, {
                setParentNextStage: this.nextStage,
                setParentPrevStage: this.previousStage,
                setParentTHBEligable: this.setTHBEligable,
                setParentTHBNotEligable: this.setTHBNotEligable,
                setUnlimited: this.setUnlimited
            });
        } else if (this.state.stage === 4) {
            active_component = React.createElement(AccountBalances, {
                setParentNextStage: this.nextStage,
                setParentPrevStage: this.previousStage,
                thb_eligible: this.state.thb_eligible,
                saveChangedValues: this.saveChangedValues,
                saveChangedDay: this.depositDayChange,
                saveChangedMonth: this.depositMonthChange,
                saveChangedYear: this.depositYearChange,
                day: this.state.day,
                month: this.state.month,
                year: this.state.year
            });
        } else if (this.state.stage === 5) {
            active_component = React.createElement(ResultsScreen, {
                user_providers: this.state.user_providers,
                thb_eligible: this.state.thb_eligible,
                day: this.state.day,
                month: this.state.month,
                year: this.state.year,
                unlimited: this.state.unlimited
            });
        }
        ;
        return (
            React.createElement("div", {className: "container-fluid"},
                React.createElement("div", {className: "row"},
                    React.createElement("div", {className: "col-md-9"},
                        React.createElement("h1", null, "How safe are your savings?"),
                        React.createElement("p", null, "Financial Services Compensation Scheme"),
                        React.createElement("p", null, "Depositor Protection for Temporary High Balances (THBs)")
                    ),
                    React.createElement("div", {className: "col-md-3"},
                        React.createElement("img", {src: "/static/img/fscs_biglogo.png", className: "img-responsive"})
                    )
                ),
                React.createElement("div", {className: "row"},
                    React.createElement("div", {className: "col-md-12"},
                        React.createElement("div", {className: "panel panel-default"},
                            React.createElement("div", {className: "panel-body"},
                                active_component
                            )
                        ),
                        React.createElement("input", {
                            type: "button",
                            className: this.state.stage > 1 ? "btn btn-default" : "btn btn-default hidden",
                            value: "Go back a step",
                            onClick: this.previousStage
                        })
                    )
                )
            )
        );
    }
});


React.render(
    React.createElement(FSCSTool, null),
    document.getElementById('fscs-tool')
);
