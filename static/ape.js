(function(win, doc, conf, version){


    /***************************************************************
     * Polyfill Functions
     ***************************************************************/


    /**
     * Get elements by class name
     * For IE <9
     */
    if(!doc.getElementsByClassName){
        doc.getElementsByClassName = function(id) {
            var
            a = [],
            r = new RegExp('(^| )'+id+'( |$)'),
            e = doc.getElementsByTagName("*"),
            i;
            for (i=0; i<e.length; i++){
                if (r.test(e[i].className)){ a[i] = e[i]; }
            }
            return a;
        }
    }


    /***************************************************************
     * APE Functions
     ***************************************************************/
    

    var

    /*
     * Initialisation Function
     * @args: arguments object defined in page
     */
    init = function(args){
    
        // Get configuration from args or default
        conf.version      = version;
        conf.customer_id  = args['customer_id'];
        conf.load         = args['load'].getTime() || (new Date).getTime();
        conf.class_prefix = args['class_prefix'] || 'ape';
        conf.debug        = args['debug']    || false;
        conf.cookie       = args['cookie']   || '_ape';
        conf.callback     = args['callback'] || '_ape.callback';
        conf.endpoint     = args['endpoint'] || 'beacon.js';

        if(conf.debug){
            win._ape.conf = conf;
        }

        // Set callback handler in global scope
        win._ape.callback = callback;

        // Build the request data payload
        payload = {
            cc: get_cookie(conf.cookie),    // The APE cookie
            db: conf.debug,                 // Debug switch
            dl: win.location.href,          // Page URL
            dr: doc.referrer,               // Referrer URL if set
            dt: doc.title,                  // Page title
            ev: 'pageload',                 // Page load event
            id: conf.customer_id,           // The customer account ID
            ld: conf.load,                  // Page load time
            lg: win.navigator.language,     // Browser language
            pc: get_placeholder_classes(),  // The set of placeholder classes on this page
            px: conf.class_prefix,          // Placeholder class prefix
            sc: win.screen.colorDepth,      // Screen colour depth
            sh: win.screen.height,          // Screen height
            sw: win.screen.width,           // Screen width
            ua: window.navigator.userAgent, // User Agent
            vr: conf.version,               // Version number of this script
            jsonp: conf.callback            // jsonp callback function
        };

        // Send page load payload to beacon endpoint
        send_beacon(payload);

    },


    /**
     * Create a cookie
     * @name:  Name of the cookie
     * @value: Value of the cookie
     * @days:  Number of days until cookie expires (optional)
     */
    set_cookie = function(name, value, days){
        var expires = "";
        if (days) {
            var date = new Date();
            date.setTime(date.getTime() + (days*86400000));
            expires = "; expires=" + date.toGMTString();
        }
        doc.cookie = name + "=" + value + expires + "; path=/";
    }


    /**
     * Get the value of a cookie
     * @name: The name of the cookie to get
     */
    get_cookie = function(name){
        var
        cookies = doc.cookie.split('; '),
        name    = name + '=';
        for (i in cookies) {
            cookie = cookies[i]
            if (cookie.indexOf(name) === 0) {
                return cookie.substring(name.length, cookie.length);
            }
        }
        return '';
    }


    /**
     * Convert a flat object in to a URI encode string
     * @obj: Object of key-value pairs to URL encode
     */
    url_serialize = function(obj) {
        var str = [];
        for (p in obj){
            if (obj.hasOwnProperty(p)) {
                str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
            }
        }
        return str.join("&");
    },


    /* Add a script tag to the document
     * @url: The url of the script
     */
    add_script_tag = function(url){
        var
        elem = doc.createElement('script'),
        node = doc.getElementsByTagName('script')[0];
        elem.type = "text/javascript";
        elem.src = url;
        node.parentNode.insertBefore(elem, node);
    },


    /* Add a style tag to the document
     * @styles: The styles
     */
    add_style_tag = function(styles){
        var
        elem = doc.createElement('style'),
        node = doc.getElementsByTagName('title')[0];
        elem.type = "text/css";
        elem.innerHTML = styles;
        node.parentNode.insertBefore(elem, node);
    },


    /*
     * Send a payload of data to the beacon end point
     * @payload: object of key-value pair data to send
     */
    send_beacon = function(payload){
        payload.rd = Math.random(); // To kick through agressive local caching
        add_script_tag(conf.endpoint + '?' + url_serialize(payload));
    },


    /**
     * Set the components on the page
     * @components an object where the key is a placeholder class and the value is html content
     */
    set_components = function(components){
        var ad_styles = "";
        for( placeholder_class in components ){
            placeholder = doc.getElementsByClassName(placeholder_class);
            for(i in placeholder){
                placeholder[i].innerHTML = components[placeholder_class].content;
            }
            ad_styles += components[placeholder_class].styles;
        }
        add_style_tag(ad_styles);
    },


    /**
     * Callback handler for interactive jsonp requests
     * @payload: The json object in the response
     */
    callback = function(payload){

        if( 'visitor_id' in payload){
            set_cookie(conf.cookie, payload.visitor_id, 90);
        }

        if( 'components' in payload ){
            set_components(payload.components);
        }
        
        if( conf.debug && console && console.log && console.error ){
            console.log(payload);
    
            if( payload.code && payload.code != 200 ){
                console.error(payload.name + ' [' + payload.code + '] ' + payload.description);
            }
        }
    },


    /**
     * Return a string of all classes assigned to placeholders on the page
     */
    get_placeholder_classes = function(){
        var
        elements = doc.getElementsByClassName(conf.class_prefix),
        classes  = []
        for( i in elements ){
            classes.push(elements[i].className);
        }
        return classes.join(' ');
    };


    /***************************************************************
     * Get on with it
     ***************************************************************/


    // Do nothing if customer_id not provided
    if (win._ape.customer_id && win._ape.customer_id != undefined){
        init(win._ape);
    }


})(window, document, {}, '0.1'); // Script version