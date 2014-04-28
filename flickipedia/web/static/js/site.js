/**
 *  Flickipedia Site javascript
 *
 *  Ryan Faulkner 2014
 */


/**
 * Class object for handling callback code
 *
 * @param numPhotos
 * @constructor
 */
function InitPageCallbacks(numPhotos) {


    /**
     *
     */
    this.titleImageHover = function() {
        $("a.title-image").hover(function() {
            // add vote selection

        }, function() {
            // remove vote selection
        });
    };

    /**
     *
     */
    this.titleImageHover = function() {
        $("." + "{{ section_img_class }}").hover(function() {
            // add vote selection
            if (!onLikeGlyph) {
                var likeGlyph = $(this).find("div.like-glyph");
                likeGlyph[0].innerHTML = '<img style="opacity:0.4; background-color:#cccccc;" src="/static/img/star.png" width="25" height="25">';
            }
        }, function() {
            // remove vote selection
            if (!onLikeGlyph) {
                var likeGlyph = $(this).find("div.like-glyph");
                likeGlyph[0].innerHTML = '';
            }
        });
    };

    /**
     *
     */
    this.titleImageHover = function() {
        $(".like-glyph").hover(function() {
            // add vote selection
            console.log(this.innerHTML);
            onLikeGlyph = true;
            this.innerHTML = '<img style="opacity:0.4; background-color:#cccccc;" src="/static/img/star_on.png" width="25" height="25">';
        }, function() {
            // remove vote selection
            onLikeGlyph = false;
            console.log(this.innerHTML);
            this.innerHTML = '';
        });
    }
}

