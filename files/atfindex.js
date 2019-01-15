/**
 * @Author:  Alemnew Asrese				
 * @emails:  alemnew.asrese@aalto.fi
 * @date:   2018-06-06
 * @note: customised from ATF-chrome-plugin by D. da Hora and A. Asrese 
 */

/*
    VERSION: 1.1;     
*/
var stats = {}

//Global variables
var output="";
// window size
var screenRect = {};
screenRect.left   = 0;
screenRect.top    = 0;
screenRect.right  = document.documentElement.clientWidth;
screenRect.bottom = document.documentElement.clientHeight;

if (!screenRect.right)  screenRect.right = 1024;
if (!screenRect.bottom) screenRect.bottom = 768;

//Function callback install
try {
    return(calculateATF());
}catch(e) {
    log(e);
}


//Main function
function calculateATF(){
    var imgs = document.getElementsByTagName("img");

    var hashImgs = {};
    var countATF = 0;
    var img_pixels = 0;

    for (i = 0; i < imgs.length; i++) {
        var rect = imgs[i].getBoundingClientRect();

        imgs[i].onscreen = intersectRect(rect, screenRect);

        if (imgs[i].onscreen) {
            imgs[i].screen_area = overlapRect(screenRect, rect);
            if (imgs[i].screen_area >= 0) countATF+=1;
            img_pixels += imgs[i].screen_area;
        }

        var key = geturlkey(imgs[i].src);
        if ( !(key in hashImgs) ) {
            hashImgs[ key ] = imgs[i]; 
        }
    }
    
    var [imgResource,jsResource,cssResource] = getResources();
    
    //Setting load time on page imgs
    for (i = 0; i < imgResource.length; i++) {
        var load_time = imgResource[i].responseEnd;

        var imgsrc = geturlkey(imgResource[i].name);
        if (imgsrc in hashImgs){
            hashImgs[ imgsrc ].loadtime = load_time;
        } 
    }


    //ATF pixel img loaded 
    img_pixels = 0; 
    var screenimgs = [];
    stats.last_img = 0.0;

    for (i = 0; i < imgs.length; i++){
        if ('loadtime' in imgs[i])
            if (imgs[i].onscreen && (imgs[i].screen_area >= 0) ) {
                screenimgs.push(imgs[i]);
                img_pixels += imgs[i].screen_area;
                if (imgs[i].loadtime > stats.last_img) stats.last_img = imgs[i].loadtime;
            }
    }
    
    stats.last_js  = 0.0;
    stats.last_css = 0.0;

    for (var i=0; i<jsResource.length; i++){
        var loadtime = jsResource[i].responseEnd;
        if (loadtime > stats.last_js) stats.last_js = loadtime;
    }

    for (var i=0; i<cssResource.length; i++){
        var loadtime = cssResource[i].responseEnd;
        if (loadtime > stats.last_css) stats.last_css = loadtime;
    }

    screenimgs.sort(function(a,b){
        return a.loadtime - b.loadtime;
    });


    var count_pixels = recordImgs(screenimgs, stats, false);

    
    var t = performance.timing;
    var web_qos = {};
    web_qos.dom = t.domContentLoadedEventEnd - t.navigationStart;
    web_qos.tcpConct = t.connectEnd - t.connectStart;
    web_qos.dnsLookup = t.domainLookupEnd - t.domainLookupStart;
    web_qos.ttfb = t.responseStart -  t.navigationStart;
    web_qos.pltStart = t.loadEventStart - t.navigationStart;
    web_qos.pltUserTime = t.loadEventEnd -  t.navigationStart;
    web_qos.requestTime = t.responseEnd - t.requestStart;
    web_qos.fetchTime = t.responseEnd -t.fetchStart;
    web_qos.serverResponseTime = t.responseStart - t.requestStart;
    if(t.secureConnectionStart == 0) {
        web_qos.tlsHandshake = 0;
    }
    else {
        web_qos.tlsHandshake = t.connectEnd - t.secureConnectionStart;
    }

    var page_img_ratio = 1.0*count_pixels / (screenRect.right * screenRect.bottom);
    
    var resources = window.performance.getEntriesByType("resource");

    var object_size = get_object_size(resources);
    var number_objects = get_number_objects(resources);

    var atf = {};
    var web_complexity = {};
    web_complexity.number_objects = number_objects;
    web_complexity.object_size = object_size;
    
    stats.web_qos = web_qos;
    stats.web_complexity = web_complexity;
    stats.count_pixels   = count_pixels;

    atf.atf            = Math.max( stats.last_img, stats.last_css, stats.last_img);
    atf.atf_integral   = stats.atf_integral;
    atf.atf_instant    = stats.atf_instant;
    atf.count_pixels   = stats.count_pixels;
    atf.ii_plt         = index_metric(resources, stats.dom, stats.plt, metric='image');
    atf.ii_atf         = index_metric(resources, stats.dom, stats.atf, metric='image');
    atf.oi_plt         = index_metric(resources, stats.dom, stats.plt, metric='object');
    atf.oi_atf         = index_metric(resources, stats.dom, stats.atf, metric='object');
    atf.bi_plt         = index_metric(resources, stats.dom, stats.plt, metric='bytes');
    atf.bi_atf         = index_metric(resources, stats.dom, stats.atf, metric='bytes');
    atf.img_atf        = screenimgs.length;
    atf.screenRect     = screenRect;
    stats.atf = atf;

    delete stats.atf_integral;
    delete stats.atf_instant;
    delete stats.count_pixels;

    return stats;

}

function get_number_objects(resources) {
    var number_objects = {};
    var  img = 0;
    var  css = 0;
    var  script = 0;
    var  misc = 0;
    var  total = resources.length;
    for (i = 0; i < total; i++) {
        if (resources[i].initiatorType == 'img') {
            img ++;
        } else if( resources[i].initiatorType == 'css') {
            css ++;
        } else if( resources[i].initiatorType == 'script') {
            script ++;
        } else {
            misc ++;
        }
    }

    number_objects.img = img;
    number_objects.css = css;
    number_objects.script = script;
    number_objects.misc = misc; 
    number_objects.total = total;

    return number_objects;

}

function get_object_size(objects) {
    var img_size = 0;
    var css_size =0;
    var script_size = 0;
    var misc_size = 0;
    var total_size = 0;
    var object_size = {}

    for (var i=0; i<objects.length; i++){ 
        var obj_type = objects[i]['initiatorType'];
        var obj_size = objects[i]['decodedBodySize']; 
        if(obj_type == 'img') {
            img_size += obj_size;
        } else if (obj_type == 'css') {
            css_size += obj_size;
        } else if (obj_type == 'script') {
            script_size += obj_size;
        } else {
            misc_size += obj_size;
        }

        total_size += obj_size;
    }

    object_size.img = img_size;
    object_size.css = css_size;
    object_size.script  = script_size;
    object_size.misc = misc_size; 
    object_size.total = total_size;

    return object_size;
}
function index_metric(objects, min_time, max_time, metric='bytes'){
    //types = img, css, link , script
    var total_cost = 0.0;
    var index      = 0.0;

    for (var i=0; i<objects.length; i++){
        var loadtime = objects[i]['responseEnd'];
        var obj_type = objects[i]['initiatorType'];
        var obj_size = objects[i]['decodedBodySize'];

        var weight = 1.0;
        if (metric == 'images' && obj_type != 'img') weight = 0.0; 

        if (loadtime < min_time) loadtime = min_time;
        if (loadtime > max_time) continue;

        if (metric == 'object')
            cost_metric = 1.0
        else
            cost_metric = obj_size;

        cost   = weight*cost_metric
        index += loadtime * cost

        total_cost+= cost
    }

    if (total_cost > 0.0){
        index /= total_cost;
    }

    return index 
}


function log(str, out="OUTPUT"){
    if (out=="DEBUG" && VERBOSITY=="DEBUG"){
        console.log(str);
    } else if (out == "WARNING" && (VERBOSITY=="WARNING" || VERBOSITY=="DEBUG")){
        output = output + "WARNING: " + str + "\n";
    } else if (out == "OUTPUT"){
        output = output + str + "\n";
    } else {
        //Suppress output
    }
}

function intersectRect(r1, r2) {
  return !(r2.left > r1.right || 
           r2.right < r1.left || 
           r2.top > r1.bottom ||
           r2.bottom < r1.top);
}

function overlapRect(r1, r2){
    x11 = r1.left;
    y11 = r1.top;
    x12 = r1.right;
    y12 = r1.bottom;
    x21 = r2.left;
    y21 = r2.top;
    x22 = r2.right;
    y22 = r2.bottom;

    x_overlap = Math.max(0, Math.min(x12,x22) - Math.max(x11,x21));
    y_overlap = Math.max(0, Math.min(y12,y22) - Math.max(y11,y21));
    return x_overlap * y_overlap;
}

function geturlkey(url){
    return url.trim().replace(/^https:/,'http:').replace(/\/$/,'').toLowerCase();
}

function getImgRes(){
    var resourceList = window.performance.getEntriesByType("resource");
    var imgResource = [];

    for (i = 0; i < resourceList.length; i++) {
        if (resourceList[i].initiatorType != "img")     continue;
        if (resourceList[i].name.match(/[.](css|js)$/)) continue;
        if (resourceList[i].name.match(/[.](css|js)[?].*$/)) continue;
        
        imgResource.push( resourceList[i] );
    }

    return imgResource;
}


//Generate new screen bitmap

function createBitmap(){
    var bitmap = new Array(screenRect.right);
    for (var i=0; i<=screenRect.right; i++){
        bitmap[i] = new Array(screenRect.bottom)
        for (var j=0; j<=screenRect.bottom; j++){
            bitmap[i][j] = null;
        }
    }   
    return bitmap;
}

/*
    There are two ways to fill the bitmap
    1 - Regular load order: Optimistic ATF integral
    2 - Reverse load order: Pessimistic ATF integral
*/
function recordImgs(screenimgs, stats, reverse){
    var count_pixels = 0;
    var count = new Array(screenimgs.length);
    var bitmap = createBitmap();

    var t = performance.timing;
    var domload = t.domContentLoadedEventEnd - t.fetchStart;
    var onload  = t.loadEventEnd             - t.fetchStart;

    for (var i =0; i<screenimgs.length; i++) {
        if (reverse){
            idx = screenimgs.length -i -1;
        } else {
            idx = i;
        }

        if ('loadtime' in screenimgs[idx]){
            var c = recordImg(screenimgs[idx], bitmap, reverse);
            count[idx] = c;
            count_pixels+=c;
        } else {
            count[idx] = 0;
        }
    }

    var atf_integral = 0.0;
    var atf_instant  = 0.0;
    var cumpixels    = 0.0;

    for (var i=0; i<screenimgs.length; i++){
        if (!('loadtime' in screenimgs[i])) continue;
        if (count[i]==0) {
           // log("Skipping image [" + i + "], loadtime " + screenimgs[i].loadtime + ": " +screenimgs[i], "WARNING");
            continue;
        }
        
        var loadtime = screenimgs[i].loadtime;  
        if(loadtime < domload) loadtime = domload;  //The minimum loadtime is the DOM PLT

        atf_integral  += (loadtime) * (1.0*count[i]/count_pixels);
        
        if (loadtime > atf_instant){
            atf_instant = screenimgs[i].loadtime;
        }
    }
    
    stats.atf_integral   = atf_integral;
    stats.atf_instant    = atf_instant;

    return count_pixels;
}

function recordImg(img, bitmap, reverse){
    var rect = img.getBoundingClientRect();
    
    var count = 0;
    if ( !('loadtime' in img) ) return 0;

    for (var i=0; i<rect.width; i++) {
        var x = Math.floor(i+rect.left);
        if(x <  0) continue;
        if(x >= screenRect.right)  continue;

        for (var j=0; j<rect.height; j++){
            var y = Math.floor(j+rect.top);
            if(y < 0) continue;
            if(y >= screenRect.bottom) continue;
            
            if( !bitmap[x][y] ) {
                bitmap[x][y] = img;
                count+=1
            } else {
                log( "Overlap at ("+x+","+y+")", "WARNING")
            }
        }
    }

    if(reverse){
        img.pessimistic = count;
    } else {
        img.optimistic  = count;
    }
        
    return count;
}


function isDict(v) {
    return typeof v==='object' && v!==null && !(v instanceof Array) && !(v instanceof Date);
}
//Recursive object clean-up for easier storage
function obj_dict(obj){

    var new_obj = {}
    for (var prop in obj){

        if ( isDict(obj[prop]) ) {
            new_obj[prop] = clean_dict(obj[prop])
        } else {

            if (obj[prop] == null) continue;
            if (obj[prop] == '') continue;
            if (obj[prop] == {}) continue;
            if (obj[prop].length == 0) continue;

            new_obj[prop] = obj[prop]
        }

    }
    return new_obj
}

function clean_dict(obj) {

    var new_obj = {}
    for (var prop in obj){

        if (obj[prop] == null) continue;
        if (obj[prop] == '') continue;
        if (obj[prop] == {}) continue;
        if (obj[prop].length == 0) continue;

    }
    return new_obj
}
function compareList(hashImgs, imgResource){
    var hashRes = {}
    for (var i =0; i<imgResource.length; i++){
        key = geturlkey(imgResource[i].name)
        if (key in hashRes){
            //hashRes[key]+=1
        } else {
            hashRes[key]=[imgResource[i],i]
        }
    }

    var imgKeys = Object.keys(hashImgs);
    var resKeys = Object.keys(hashRes);

    
    //Comparing a to b:
    var count_no_img = 0;
    var count_no_res = 0;

    for (var i=0;i<imgKeys.length;i++){
        key = imgKeys[i];
        if ( !(key in hashRes) ){
            count_no_img += 1;
        }
    }

    for (var i=0; i<resKeys.length; i++ ){
        key = resKeys[i];
        if ( !(key in hashImgs) ){
            count_no_res += 1;
            res = hashRes[key];
        }
    }

}

//Return: IMG, JS, CSS;
function getResources(){
    var resourceList = window.performance.getEntriesByType("resource");
    var imgResource = [];
    var jsResource  = [];
    var cssResource = [];
    var not_added = 0

    for (i = 0; i < resourceList.length; i++) {
        var added = false;

        if ( (resourceList[i].initiatorType == "img") &&
        !(resourceList[i].name.match(/[.](css|js)$/)) &&
        !(resourceList[i].name.match(/[.](css|js)[?].*$/))){
            added = true;
            imgResource.push( resourceList[i] );
        }

        //CSS detection
        if ( (resourceList[i].initiatorType == "link") ||
            ((resourceList[i].initiatorType == "css")) ||
            (resourceList[i].name.match(/[.](css)/)) ) {
            if (added) log("Re-added as CSS "+i+": " + resourceList[i].initiatorType + ": " + resourceList[i].name);
            added = true;
            cssResource.push( resourceList[i] );
        }

        if ((resourceList[i].initiatorType == "script")) //|| (resourceList[i].name.match(/[.](js)$/))
        {
            if (added) log("Re-added as JS "+i+": " + resourceList[i].initiatorType + ": " + resourceList[i].name);
            added = true;
            jsResource.push( resourceList[i] );
        }

        if (added == false){
            log("Not added: " + resourceList[i].initiatorType + ": " + resourceList[i].name);
            not_added+=1;
        }
    }

    log("All resources found: " + resourceList.length)
    log("Image resources found: " + imgResource.length);
    log("CSS resources found: " + jsResource.length);
    log("JS resources found: " + cssResource.length);
    log("NOT added: " + not_added);

    return [imgResource, jsResource, cssResource];
}

function getParameterOrNull(obj, parameter){
    if (parameter in obj){
        return obj[parameter];
    } else {
        return 'null';
    }
}

function imageProfile(imgs, stats){
    
    var imglist = [];
    for (var i = 0; i<imgs.length; i++) {
        imgd = {}
        
        imgd.src         = imgs[i].src;
        imgd.name        = geturlkey(imgs[i].src);
        imgd.rect        = imgs[i].getBoundingClientRect();
        imgd.x           = getParameterOrNull(imgs[i],'x');
        imgd.y           = getParameterOrNull(imgs[i],'y');
        imgd.width       = getParameterOrNull(imgs[i],'width');
        imgd.height      = getParameterOrNull(imgs[i],'height');
        imgd.loadtime    = getParameterOrNull(imgs[i],'loadtime');
        imgd.optimistic  = getParameterOrNull(imgs[i],'optimistic');
        imgd.pessimistic = getParameterOrNull(imgs[i],'pessimistic');

        imglist.push(imgd);
    }
    
    stats.imgs = imglist;
}


