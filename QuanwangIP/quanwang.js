$(function () {
    $('.port')['each'](function () {
        var a = $(this)['html']();
        if (a['indexOf']('*') != -0x1) {
            return
        }
        ;var b = $(this)['attr']('class');
        try {
            b = (b['split'](' '))[0x1];
            var c = b['split']('');
            var d = c['length'];
            var f = [];
            for (var g = 0x0; g < d; g++) {
                f['push']('ABCDEFGHIZ'['indexOf'](c[g]))
            }
            ;$(this)['html'](window['parseInt'](f['join']('')) >> 0x3)
        } catch (e) {
        }
    })
})