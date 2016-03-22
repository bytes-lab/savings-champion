(function($){
	var defaults = {
        'pane_selector': '.pane',
        'nav_selector': '#decision-nav li',
        'next_link': 'a.next'
    };
	/**
	 * Find a link within target, use that if user clicks on target
	 */
	$.fn.decision_tree = function(opts){
		 var options = $.extend({}, defaults, opts);
		 return this.each(function () {
			var $base = $(this);

			$(options.next_link, $base).bind('click', function(event){
				event.preventDefault();
				// check if visible fields are completed satisfactorily
				var next_pane_selector = $(this).attr('href');

				var $current_pane = $(this).parents(options.pane_selector);

				if(next_pane_selector.charAt(0)=="#") {
					// simulate the click so we use the same code
					$('a[href="' + next_pane_selector + '"]', options.nav_selector).click();
				}
			});

			// handling the navigaion through here as well
			$(options.nav_selector, $base).each(function(){
				$('a', $(this)).bind('click', function(event){
					event.preventDefault();

					$(options.pane_selector, $base).hide();

					var next_pane_selector = $(this).attr('href');
					$(this).parent('li').addClass('active');

					$(next_pane_selector).fadeIn();

					return false;
				});
			});

		 });
	};
})(jQuery);
