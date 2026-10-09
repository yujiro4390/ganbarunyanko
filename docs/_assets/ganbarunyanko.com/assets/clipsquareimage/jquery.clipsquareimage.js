/**
 * clipsquareimage.js
 * ver.201611070000
*/

;(function($) {
    'use strict';

    $.fn.clipSquareImage = function(options) {
        var settings = $.extend({
            'adjustParentHeight': false
        }, options);

        return this.each(function() {
            var $this = $(this);
            var clipWidth = $this.parent().width();
            var clipHeight = (settings.adjustParentHeight) ? $this.parent().height() : clipWidth;
            var ratio, imageWidth, imageHeight, posLeft, posTop;

            $this.parent().css({
                'position': 'relative',
                'display': 'block',
                'height': clipHeight,
                'overflow': 'hidden'
            });

            // 画像style
            // "width: 100%"で仮リサイズ
            $this.css({
                'display': 'block',
                'position': 'absolute',
                'left': '0',
                'top': '0',
                'width': '100%',
                'height': 'auto',
                'margin': '0',
                'padding': '0',
                'max-width': 'none'
            });

            // clip高 > image高 → clip高でリサイズ
            if (clipHeight > $this.height()) {
                ratio = clipHeight / $this.height();
                imageWidth = Math.floor($this.width() * ratio);
                imageHeight = clipHeight;
                posLeft = - (imageWidth - clipWidth) / 2;
                posTop = 0;

            // clip高 < image高 → clip幅でリサイズ
            } else {
                ratio = clipWidth / $this.width();
                imageWidth = clipWidth;
                imageHeight = Math.floor($this.height() * ratio);
                posLeft = 0;
                posTop = - (imageHeight - clipHeight) / 2;
            }

            $this.css({
                'width': imageWidth + 'px',
                'height': imageHeight + 'px',
                'left': posLeft + 'px',
                'top': posTop + 'px'
            });

        });
    };
}(jQuery));
