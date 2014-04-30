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
    this.sectionImageHover = function(idx) {
        console.log("#" + sectionImageHandle + "-" + idx);
        $("#" + sectionImageHandle + "-" + idx).hover(function() {
            // add vote selection
            if (!onLikeGlyph) {
                var likeGlyph = $(this).find("div.like-glyph");
                likeGlyph[0].innerHTML = '<img style="opacity:0.4; background-color:#cccccc;" src="/static/img/star.png" width="25" height="25">';
            }
        }, function() {
            // remove vote selection
            if (!onLikeGlyph) {
                var likeGlyph = $(this).find("div.like-glyph-" + idx);
                likeGlyph[0].innerHTML = '';
            }
        });
    };

    /**
     *
     */
    this.likeGlyphImageHover = function(idx) {
        console.log("#like-glyph-" + idx);
        $("#like-glyph-" + idx).hover(function() {
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
    };

    for (var i = 1; i < numPhotos; i++) {
        this.sectionImageHover(i);
        this.likeGlyphImageHover(i);
    }
}

