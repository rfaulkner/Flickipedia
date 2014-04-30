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
function InitPageCallbacks(numPhotos, sectionImageHandle) {


    var onLikeGlyph = [];

    /**
     *  Handle hover events on the title image
     */
    this.titleImageHover = function() {
        $("a.title-image").hover(function() {
            // add vote selection

        }, function() {
            // remove vote selection
        });
    };

    /**
     *  Handle hover events on the section images
     */
    this.sectionImageHover = function(idx) {
        $("#" + sectionImageHandle + "-" + idx).hover(function() {
            // add vote selection
            if (!onLikeGlyph[idx]) {
                var likeGlyph = $(this).find("div.like-glyph");
                likeGlyph[0].innerHTML = '<img style="opacity:0.4; background-color:#cccccc;" src="/static/img/star.png" width="25" height="25">';
            }
        }, function() {
            // remove vote selection
            if (!onLikeGlyph[idx]) {
                var likeGlyph = $(this).find("div.like-glyph");
                likeGlyph[0].innerHTML = '';
            }
        });
    };

    /**
     *  Handle hover events on the like glyphs
     */
    this.likeGlyphImageHover = function(idx) {
        $("#like-glyph-" + idx).hover(function() {
            // add vote selection
            if (!onLikeGlyph[idx]) {
                onLikeGlyph[idx] = true;
                this.innerHTML = '<img style="opacity:0.4; background-color:#cccccc;" src="/static/img/star_on.png" width="25" height="25">';
            }
        }, function() {
            // remove vote selection
            if (onLikeGlyph[idx]) {
                onLikeGlyph[idx] = false;
                this.innerHTML = '';
            }
        });
    };

    for (var i = 0; i < numPhotos; i++) {
        onLikeGlyph[i] = false;
        this.sectionImageHover(i);
        this.likeGlyphImageHover(i);
    }
}

