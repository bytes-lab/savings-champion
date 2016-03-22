
/**
jQuery Formset 1.3-pre
@author Stanislaus Madueke (stan DOT madueke AT gmail DOT com)
@requires jQuery 1.2.6 or later

Copyright (c) 2009, Stanislaus Madueke
All rights reserved.

Licensed under the New BSD License
See: http://www.opensource.org/licenses/bsd-license.php
 */

(function() {
  (function($) {
    $.fn.formset = function(opts) {
      var $$, options;
      $$ = $(this);
      options = $.extend({}, $.fn.formset.defaults, opts);
      return $$.each(function(i) {
        var addButton, applyExtraClasses, buttonRow, childElementSelector, del, flatExtraClasses, hasChildElements, hideAddButton, insertDeleteLink, maxForms, numCols, row, showAddButton, template, totalForms, updateElementIndex;
        flatExtraClasses = options.extraClasses.join(" ");
        totalForms = $("#id_" + options.prefix + "-TOTAL_FORMS");
        maxForms = $("#id_" + options.prefix + "-MAX_NUM_FORMS");
        childElementSelector = "input,select,textarea,label,div";
        applyExtraClasses = function(row, ndx) {
          if (options.extraClasses) {
            row.removeClass(flatExtraClasses);
            row.addClass(options.extraClasses[ndx % options.extraClasses.length]);
          }
        };
        updateElementIndex = function(elem, prefix, ndx) {
          var idRegex, replacement;
          idRegex = new RegExp(prefix + "-(\\d+|__prefix__)-");
          replacement = prefix + "-" + ndx + "-";
          if (elem.attr("for")) {
            elem.attr("for", elem.attr("for").replace(idRegex, replacement));
          }
          if (elem.attr("id")) {
            elem.attr("id", elem.attr("id").replace(idRegex, replacement));
          }
          if (elem.attr("name")) {
            elem.attr("name", elem.attr("name").replace(idRegex, replacement));
          }
        };
        hasChildElements = function(row) {
          return row.find(childElementSelector).length > 0;
        };
        showAddButton = function() {
          return maxForms.length === 0 || (maxForms.val() === "" || (maxForms.val() - totalForms.val() > 0));
        };
        insertDeleteLink = function(row) {
          var addCssSelector, delCssSelector;
          delCssSelector = options.deleteCssClass.trim().replace(/\s+/g, ".");
          addCssSelector = options.addCssClass.trim().replace(/\s+/g, ".");
          if (row.is("TR")) {
            row.children(":last").append("<a class=\"" + options.deleteCssClass + "\" href=\"javascript:void(0)\">" + options.deleteText + "</a>");
          } else if (row.is("UL") || row.is("OL")) {
            row.append("<li><a class=\"" + options.deleteCssClass + "\" href=\"javascript:void(0)\">" + options.deleteText + "</a></li>");
          } else {
            row.append("<a class=\"" + options.deleteCssClass + "\" href=\"javascript:void(0)\">" + options.deleteText + "</a>");
          }
          row.find("a." + delCssSelector).click(function() {
            var buttonRow, del, formCount, forms;
            row = $(this).parents("." + options.formCssClass);
            del = row.find("input:hidden[id $= \"-DELETE\"]");
            buttonRow = row.siblings("a." + addCssSelector + ", ." + options.formCssClass + "-add");
            forms = void 0;
            if (del.length) {
              del.val("on");
              row.hide();
              forms = $("." + options.formCssClass).not(":hidden");
            } else {
              row.remove();
              forms = $("." + options.formCssClass).not(".formset-custom-template");
              totalForms.val(forms.length);
            }
            i = 0;
            formCount = forms.length;
            while (i < formCount) {
              applyExtraClasses(forms.eq(i), i);
              if (!del.length) {
                forms.eq(i).find(childElementSelector).each(function() {
                  updateElementIndex($(this), options.prefix, i);
                });
              }
              i++;
            }
            if (buttonRow.is(":hidden") && showAddButton()) {
              buttonRow.show();
            }
            if (options.removed) {
              options.removed(row);
            }
            return false;
          });
        };
        row = $(this);
        del = row.find("input:checkbox[id $= \"-DELETE\"]");
        if (del.length) {
          if (del.is(":checked")) {
            del.before("<input type=\"hidden\" name=\"" + del.attr("name") + "\" id=\"" + del.attr("id") + "\" value=\"on\" />");
            row.hide();
          } else {
            del.before("<input type=\"hidden\" name=\"" + del.attr("name") + "\" id=\"" + del.attr("id") + "\" />");
          }
          $("label[for=\"" + del.attr("id") + "\"]").hide();
          del.remove();
        }
        if (hasChildElements(row)) {
          row.addClass(options.formCssClass);
          if (row.is(":visible")) {
            insertDeleteLink(row);
            applyExtraClasses(row, i);
          }
        }
        if ($$.length) {
          hideAddButton = !showAddButton();
          if (options.formTemplate) {
            template = (options.formTemplate instanceof $ ? options.formTemplate : $(options.formTemplate));
            template.removeAttr("id").addClass(options.formCssClass + " formset-custom-template");
            template.find(childElementSelector).each(function() {
              updateElementIndex($(this), options.prefix, "__prefix__");
            });
            insertDeleteLink(template);
          } else {
            template = $("." + options.formCssClass + ":last").clone(true).removeAttr("id");
            template.find("input:hidden[id $= \"-DELETE\"]").remove();
            template.find(childElementSelector).not(options.keepFieldValues).each(function() {
              var elem;
              elem = $(this);
              if (elem.is("input:checkbox") || elem.is("input:radio")) {
                elem.attr("checked", false);
              } else {
                elem.val("");
              }
            });
          }
          options.formTemplate = template;
          if ($$.is("TR")) {
            numCols = $$.eq(0).children().length;
            buttonRow = $("<tr><td colspan=\"" + numCols + "\"><a class=\"" + options.addCssClass + "\" href=\"javascript:void(0)\">" + options.addText + "</a></tr>").addClass(options.formCssClass + "-add");
            $$.parent().append(buttonRow);
            if (hideAddButton) {
              buttonRow.hide();
            }
            addButton = buttonRow.find("a");
          } else {
            $$.filter(":last").after("<a class=\"" + options.addCssClass + "\" href=\"javascript:void(0)\">" + options.addText + "</a>");
            addButton = $$.filter(":last").next();
            if (hideAddButton) {
              addButton.hide();
            }
          }
          addButton.click(function() {
            var formCount;
            formCount = parseInt(totalForms.val());
            row = options.formTemplate.clone(true).removeClass("formset-custom-template");
            buttonRow = $($(this).parents("tr." + options.formCssClass + "-add").get(0) || this);
            applyExtraClasses(row, formCount);
            row.insertBefore(buttonRow).show();
            row.find(childElementSelector).each(function() {
              updateElementIndex($(this), options.prefix, formCount);
            });
            totalForms.val(formCount + 1);
            if (!showAddButton()) {
              buttonRow.hide();
            }
            if (options.added) {
              options.added(row);
            }
            return false;
          });
        }
      });
    };
    $.fn.formset.defaults = {
      prefix: "form",
      formTemplate: null,
      addText: "add another",
      deleteText: "remove",
      addCssClass: "add-row",
      deleteCssClass: "delete-row",
      formCssClass: "dynamic-form",
      extraClasses: [],
      keepFieldValues: "",
      added: null,
      removed: null
    };
  })(jQuery);

}).call(this);

//# sourceMappingURL=jquery.formset.js.map
