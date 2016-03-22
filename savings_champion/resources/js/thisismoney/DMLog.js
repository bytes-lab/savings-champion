var DM_log = function(c, o) {
    'use strict';
    // Logger for Daily mail
    o = o || {};

    var loc = document.location;
    var getParam = function(p) {
        var pairs = (loc.href.split('?')[1] || '').split('&'), l = pairs.length;
        while (0 < l) {
            l--;
            if (pairs[l].split('=')[0].toLowerCase() === p) {
                return pairs[l].split('=')[1];
            }
        }
        return null;
    };

    // set up SCode properties
    //if (!o.pageName) o.pageUrl = loc.href.split('?')[0];
    o.domain = o.domain || loc.hostname;
    o.prop4 = o.prop4 || 'partnerpage';
    o.ito = o.ito || getParam('ito');

    // use iframe to make call
    document.write('<iframe id="DMLog" height="1" width="1" frameborder="0" src="javascript:false;" style="position:absolute;left:-1000px;"></iframe>');
    setTimeout(function() {
        var el = document.getElementById('DMLog'), s = '';
        for (var x in o) {
            if (o[x]) {
                s += '&' + x + '=' + encodeURIComponent(o[x]);
            }
        }
        el.src = 'http://www.dailymail.co.uk/' + c + '/index.html?headeronly=true&decorator=headeronly' + s;
    }, 10);

};
