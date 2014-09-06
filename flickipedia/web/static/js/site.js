/**
 *  Flickipedia Site javascript
 *
 *  Ryan Faulkner 2014
 */


/**
 * Builds the glyph-image element based on state
 *
 * @param path          relative path of image file
 * @param isHover       is the glyph element under the pointer?
 * @param isSelected    has this element been selected by the user?
 * @param width         [optional] width of glyph
 * @param height        [optional] height of glyph
 *
 * @returns {string}    Markup for the glyph image element
 */
function getGlyphImageState(path, isHover, isSelected, width, height) {

    if (width == undefined) { width = 25; }
    if (height== undefined) { height = 25; }

    var sizeStyle = 'width="' + width + '" height="' + height + '">';

    if (!isHover && !isSelected) {
        return '<img style="float:left; opacity:0.4; background-color:#cccccc;" src="/static/img/' + path + '"' + sizeStyle;
    } else if (isHover && !isSelected) {
        return '<img style="float:left; opacity:0.6; background-color:#cccccc;" src="/static/img/' + path + '"' + sizeStyle;
    } else if (!isHover && isSelected) {
        return '<img style="float:left; opacity:0.8; background-color:#cccccc;" src="/static/img/' + path + '"' + sizeStyle;
    } else {
        return '<img style="float:left; opacity:0.8; background-color:#cccccc;" src="/static/img/' + path + '"' + sizeStyle;
    }
}

/**
 * Class object for handling callback code
 *
 * @param photos
 * @param article
 * @param user
 * @param numPhotos
 * @param sectionImageHandle
 * @constructor
 */
function InitPageCallbacks(
    photos,
    article,
    user,
    numPhotos,
    sectionImageHandle) {

    var onLinkGlyph = [];   // Flags indicating when hovering over "link" glyph
    var onVoteGlyph = [];   // Flags indicating when hovering over "vote" glyph
    var isEndorsed = [];    // Flags indicating which photos have been endorsed
    var isExcluded = [];    // Flags indicating which photos have been excluded


    /**
     * Handle hover events on the section images
     *
     * @param idx
     * @param params
     */
    this.sectionImageHover = function(idx, params) {
        $("#" + sectionImageHandle + "-" + idx).hover(function() {

            var linkGlyph = $(this).find("a");
            var endorseCount = 0;
            var excludeCount = 0;

            linkGlyph[0].innerHTML = getGlyphImageState('link.png', true, false);

            if (!onVoteGlyph[idx]) {

                var content = '';
                var endorseGlyph = $(this).find("div.endorse");
                var excludeGlyph = $(this).find("div.exclude");
                var endorseCountGlyph = $(this).find("div.endorsecount");
                var excludeCountGlyph = $(this).find("div.excludecount");

                // Determine whether this user likes the photo
                $.getJSON('rest/api_photo_endorse_fetch' + '?' + params, function(data) {
                    isEndorsed[idx] = parseInt(data['endorse-fetch']);
                }).done(function() {
                    endorseGlyph[0].innerHTML = getGlyphImageState('endorse.png', false, isEndorsed[idx]);
                });

                $.getJSON('rest/api_photo_exclude_fetch' + '?' + params, function(data) {
                    isExcluded[idx] = parseInt(data['exclude-fetch']);
                }).done(function() {
                    excludeGlyph[0].innerHTML = getGlyphImageState('unendorse.png', false, isExcluded[idx]);
                });

                $.getJSON('rest/api_photo_endorse_count' + '?' + params, function(data) {
                    endorseCount = data['endorse-count'];
                }).done(function() {
                    content = '<table border="0" cellpadding="0" cellspacing="0"><tr><td width="25" height="25" style="opacity:0.3;" background="/static/img/blank.png" valign="bottom"> +' + endorseCount + '</td></tr></table>';
                    endorseCountGlyph[0].innerHTML = '<div class="counter">' + content + '</div>';
                });

                $.getJSON('rest/api_photo_exclude_count' + '?' + params, function(data) {
                    excludeCount = data['exclude-count'];
                }).done(function() {
                    content = '<table border="0" cellpadding="0" cellspacing="0"><tr><td width="25" height="25" style="opacity:0.3;" background="/static/img/blank.png" valign="bottom"> ' + excludeCount + '</td></tr></table>';
                    excludeCountGlyph[0].innerHTML = '<div class="counter">' + content + '</div>';
                });
            }
        }, function() {
            var linkGlyph = $(this).find("a");
            linkGlyph[0].innerHTML = getGlyphImageState('link.png', true, false);

            if (!onVoteGlyph[idx]) {
                var endorseGlyph = $(this).find("div.endorse");
                var exludeGlyph = $(this).find("div.exclude");
                var endorseCountGlyph = $(this).find("div.endorsecount");
                var excludeCountGlyph = $(this).find("div.excludecount");

                endorseGlyph[0].innerHTML = '';
                exludeGlyph[0].innerHTML = '';
                endorseCountGlyph[0].innerHTML = '';
                excludeCountGlyph[0].innerHTML = '';
            }
        });
    };

    /**
     *  Handle hover events on the like glyphs
     */
    this.voteGlyphImageHover = function(idx) {
        $("#vote-glyph-" + idx).hover(function() {
            if (!onVoteGlyph[idx]) {
                var endorseGlyph = $(this).find("div.endorse");
                var excludeGlyph = $(this).find("div.exclude");

                endorseGlyph[0].innerHTML = getGlyphImageState('endorse.png', true, isEndorsed[idx]);
                excludeGlyph[0].innerHTML = getGlyphImageState('unendorse.png', true, isExcluded[idx]);

                onVoteGlyph[idx] = true;
            }
        }, function() {
            var endorseGlyph = $(this).find("div.endorse");
            var excludeGlyph = $(this).find("div.exclude");
            var endorseCountGlyph = $(this).find("div.endorsecount");
            var excludeCountGlyph = $(this).find("div.excludecount");

            endorseGlyph[0].innerHTML = '';
            excludeGlyph[0].innerHTML = '';
            endorseCountGlyph[0].innerHTML = '';
            excludeCountGlyph[0].innerHTML = '';

            onVoteGlyph[idx] = false;
        });
    };

    /**
     * Handle click events on the endorse glyph. These events will allow users to toggle
     * whether they endorse the photo for inclusion
     *
     * @param idx       int, index on this article
     * @param params
     */
    this.endorseGlyphImageClick = function(idx, params) {
        $("#endorse-" + idx).click(function() {
            $.getJSON('rest/api_photo_endorse_event' + '?' + params, function(data) {
                isEndorsed[idx] = isEndorsed[idx] ? false : true;
                this.innerHTML = getGlyphImageState('endorse.png', true, isEndorsed[idx]);
            }.bind(this));
        });
    };

    /**
     * Handle click events on the exclude glyph. These events will allow users to toggle
     * whether they endorse the photo for exclusion
     *
     * @param idx       int, index on this article
     * @param params
     */
    this.excludeGlyphImageClick = function(idx, params) {
        $("#exclude-" + idx).click(function() {
            $.getJSON('rest/api_photo_exclude_event' + '?' + params, function(data) {
                isExcluded[idx] = isExcluded[idx] ? false : true;
                this.innerHTML = getGlyphImageState('unendorse.png', true, isExcluded[idx]);
            }.bind(this));
        });
    };

    /**
     * Iterate over all photos selected for the article and initialize data structures
     * & call back functions
     */
    for (var i = 0; i < numPhotos; i++) {
        onVoteGlyph[i] = false;
        onLinkGlyph[i] = false;

        isEndorsed[i] = false;
        isExcluded[i] = false;

        this.sectionImageHover(i, 'photo-id=' + photos[i] + '&article-id=' + article + '&user-id=' + user);
        this.voteGlyphImageHover(i);
        this.endorseGlyphImageClick(i, 'photo-id=' + photos[i] + '&article-id=' + article + '&user-id=' + user);
        this.excludeGlyphImageClick(i, 'photo-id=' + photos[i] + '&article-id=' + article + '&user-id=' + user);
    }
}

