/**
    * @package Rocket Creative Multipurpose HTML Template
    * 
    * Template Scripts
    * Created by Dan Fisher
*/

;(function($){
  "use strict";


  $(window).load(function() {
    // Page loader
    $(".page-loader div").delay(0).fadeOut();
    $(".page-loader").delay(200).fadeOut("slow");
  });

  // Check for Mobile Devices
  var isMobile;
  if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
    isMobile = true;
    $("html").addClass("mobile");
  } else {
    isMobile = false;
    $("html").addClass("no-mobile");
  }

  var Core = {

    initialize: function() {

      //Main Navigation
      this.MainNav(); 

      //Mansory Blog
      this.MasonryBlog();

      //Mansory Gallery
      this.MasonryGallery();

      //Magnific Popup (Gallery)
      this.MagnificPopupGallery();

      //Magnific Popup
      this.MagnificPopup();

      //Product Gallery
      this.ProductGallery();

      //Back To Top
      this.BackToTop();

      //Parallax Background
      this.ParallaxBackground();

      //Countdown
      this.CountDown();

      //Countdown Event
      this.CountDownEvent();

      //Animation on Scroll
      this.AnimationOnScroll();

      //Progress Bar Animation
      this.ProgressAnimate();

      //Make scroll smoother an faster
      // this.fixScroll();

      //Count our numbers
      this.counterTo();

      //Flickr
      this.flickrFeed();

      //Carousel
      this.carouselSlider();

      //Range Slider
      this.rangeSlider();

      //Tooltip
      this.tooltipScript();

      //Custom Select
      this.customSelect();

      //Social Links
      this.socialLinksTrigger();

      //Loading Button
      this.loadingButton();

      //Filter Button
      this.filterButton();

      //Gallery Filter
      this.galleryFilter();

      //Scroll Navigation
      this.scrollNav();

      //Sticky Header
      this.stickyHeader();

      //Google Map Address
      this.GMapAddress();

    },

    MainNav: function(){
      // Menu drop down effect
      $('.dropdown-toggle').dropdownHover().dropdown();
      $(document).on('click', '.fhmm .dropdown-menu', function(e) {
          e.stopPropagation()
      });

      $('.navbar-toggle').on('click', function () {
        $('.navbar-collapse').collapse('toggle');
      });
    },

    MasonryBlog: function(){
      // Isotope containers
      var $container = $('.masonry-feed');

      // initialize Isotope after all images have loaded
      $container.imagesLoaded( function() {
        var $filter = $('.tags-filter');

        // bind filter on select change
        $('.filter-categories').on( 'change', function() {
          var filterValue = this.value;
          $container.isotope({ filter: filterValue });
        });

        $container.isotope({
          filter              : '*',
          resizable           : false,
          layoutMode:         'masonry',
          itemSelector:       '.masonry-item'
        });

        // filter items on button click
        $filter.on( 'click', 'a', function() {
          var filterValue = $(this).attr('data-filter');
          $filter.find('a').removeClass('btn-primary').addClass('btn-default');
          $(this).addClass('btn-primary').removeClass('btn-default');
          $container.isotope({ 
              filter: filterValue
          });
          return false;
        });

      });
    },

    MasonryGallery: function(){
      // Isotope containers
      var $container = $('.js_gallery-feed');

      // initialize Isotope after all images have loaded
      $container.imagesLoaded( function() {
        var $filter = $('.gallery-filter');

        $container.isotope({
          filter              : '*',
          resizable           : false,
          layoutMode:         'fitRows',
          itemSelector:       '.gallery-item'
        });

        // filter items on button click
        $filter.on( 'click', 'a', function() {
          var filterValue = $(this).attr('data-filter');
          var filterHtml = $(this).clone();
          $filter.find('a').removeClass('btn-primary').addClass('btn-default');
          $(this).addClass('btn-primary').removeClass('btn-default');
          $container.isotope({ 
              filter: filterValue
          });
          $(".filter-clone-btn").html(filterHtml);
          return false;
        });

      });
    },

    MagnificPopupGallery: function(){
      $('.magnific-popup__custom-title').magnificPopup({
        type:'image',
        // Delay in milliseconds before popup is removed
        removalDelay: 300,

        gallery:{
          enabled:true
        },
        // Class that is added to popup wrapper and background
        // make it unique to apply your CSS animations just to this exact popup
        mainClass: 'mfp-fade',

        callbacks: {
          markupParse: function(template, values, item) {
           values.title = item.el.data('desc');
          }
        },
        autoFocusLast: false,

        titleSrc: function(item) {
          return item.el.attr('title');
        }
      });
    },

    MagnificPopup: function(){
      $('.magnific-popup-link').magnificPopup({
        type:'image',
        // Delay in milliseconds before popup is removed
        removalDelay: 300,

        gallery:{
          enabled:true
        },
        // Class that is added to popup wrapper and background
        // make it unique to apply your CSS animations just to this exact popup
        mainClass: 'mfp-fade',
        autoFocusLast: false,
        
      });
    },

    ProductGallery: function(){
      $('#product-gallery').royalSlider({
        fullscreen: {
          enabled: false,
          nativeFS: true
        },
        controlNavigation: 'thumbnails',
        thumbs: {
          orientation: 'vertical',
          spacing: 20,
          firstMargin: false,
          appendSpan: true,
          arrows: false,
          autoCenter: true
        },
        transitionType:'fade',
        autoScaleSlider: true, 
        autoScaleSliderWidth: 570,     
        autoScaleSliderHeight: 550,
        loop: true,
        arrowsNav: false,
        keyboardNavEnabled: true

      });
    },

    BackToTop: function(){
      // Back to Top
      $("#back-top").hide();
      
      $(window).scroll(function () {
        if ($(this).scrollTop() > 100) {
            $('#back-top').fadeIn();
        } else {
            $('#back-top').fadeOut();
        }
      });
    },

    ParallaxBackground: function(){
      // Parallax        
      if (($(window).width() >= 1024) && (isMobile == false)) {
        $(".parallax-bg").each(function() {
          $(this).parallax("50%", 0.2);
        });
      }
    },

    CountDown: function(){
      $("#countdown").countdown({
        date: "december 1, 2015 09:59",
        dayText: '',
        daySingularText: '',
        hourText: '',
        hourSingularText: '',
        minText: '',
        minSingularText: '',
        secText: '',
        secSingularText: '',
        template: "<div id='days' class='holder col-sm-3'><div class='days-count number'>%d</div><div class='days-label desc'>days</div></div><div id='hours' class='holder col-sm-3'><div class='hours-count number'>%h</div><div class='hours-label desc'>hours</div></div><div id='mins' class='holder col-sm-3'><div class='mins-count number'>%i</div><div class='mins-label desc'>minutes</div></div><div id='secs' class='holder col-sm-3'><div class='secs-count number'>%s</div><div class='secs-label desc'>seconds</div></div>"
      });
    },

    CountDownEvent: function(){
      $("#countdown_event").countdown({
        date: "december 1, 2015 09:59",
        dayText: '',
        daySingularText: '',
        hourText: '',
        hourSingularText: '',
        minText: '',
        minSingularText: '',
        secText: '',
        secSingularText: '',
        template: "<div id='days' class='holder col-sm-3'><div class='days-count number'>%d</div><div class='days-label desc'>days</div></div><div id='hours' class='holder col-sm-3'><div class='hours-count number'>%h</div><div class='hours-label desc'>hours</div></div><div id='mins' class='holder col-sm-3'><div class='mins-count number'>%i</div><div class='mins-label desc'>minutes</div></div><div id='secs' class='holder col-sm-3'><div class='secs-count number'>%s</div><div class='secs-label desc'>seconds</div></div>"
      });
    },

    AnimationOnScroll: function(){
      var wow = new WOW(
        {
          boxClass:     'wow',      // animated element css class (default is wow)
          animateClass: 'animated', // animation css class (default is animated)
          offset:       100,          // distance to the element when triggering the animation (default is 0)
          mobile:       false,      // trigger animations on mobile devices (default is true)
          live:         true,       // act on asynchronously loaded content (default is true)
          callback:     function(box) {
            // the callback is fired every time an animation is started
            // the argument that is passed in is the DOM node being animated
          }
        }
      );
      wow.init();
    },


    ProgressAnimate: function(){

      $(".progress .progress-bar").progressbar();

    },


    fixScroll: function(){

      var body = document.body,
        timer;

      window.addEventListener('scroll', function() {
        clearTimeout(timer);
        if(!body.classList.contains('disable-hover')) {
          body.classList.add('disable-hover')
        }
        
        timer = setTimeout(function(){
          body.classList.remove('disable-hover')
        },200);
      }, false);

    },


    counterTo: function(){

      $(".counter[data-to]").countTo({
        speed: 4000,
        refreshInterval: 30
      });

    },


    flickrFeed: function(){

      $('.flickr-feed').jflickrfeed({
        limit: 9,
        qstrings: {
          id: '52617155@N08'
        },
        itemTemplate: '<li><a href="{{link}}" target="_blank"><img src="{{image_s}}" alt="{{title}}" /></a></li>'
      });

    },


    carouselSlider: function(){

      // Widget Carousel
      $(".js_widget-carousel").owlCarousel({
        loop:true,
        margin:0,
        nav:true,
        dots:false,
        responsive:{
          0:{
              items:1
          }
        },
        navText : ["<span class='dotted-link2'><i class='fa fa-chevron-left'></i> <span>Prev</span></span>","<span class='dotted-link2'><span>Next</span> <i class='fa fa-chevron-right'></i></span>"]
      });

      // One Slider
      $(".js_one-slide").owlCarousel({
        loop:true,
        margin:0,
        nav:true,
        dots:false,
        responsive:{
          0:{
              items:1
          }
        },
        navText : ["<span class='btn btn-primary btn-single-icon'><i class='fa fa-chevron-left'></i></span>","<span class='btn btn-primary btn-single-icon'><i class='fa fa-chevron-right'></i></span>"]
      });

      // Team Slider
      $(".js_team-slider").owlCarousel({
        loop:true,
        margin:10,
        nav:true,
        dots:true,
        responsive:{
          0:{
              items:1
          },
          768:{
              items:1
          },
          992:{
              items:2
          },
          1200:{
              items:2
          }
        },
        navText : ["<span class='link-circle'><i class='fa fa-angle-left'></i></span>","<span class='link-circle'><i class='fa fa-angle-right'></i></span>"]
      });

      // Logo Slider
      $(".js_logo-slider").owlCarousel({
        loop:true,
        margin:10,
        nav:false,
        dots:false,
        responsive:{
          0:{
              items:2
          },
          768:{
              items:2
          },
          992:{
              items:2
          }
        }
      });

      // Logo Slider (autoplay)
      $(".js_logo-slider_autoplay").owlCarousel({
        autoplay:true,
        autoplayTimeout:5000,
        autoplayHoverPause:true,
        loop:true,
        margin:10,
        nav:false,
        dots:false,
        responsive:{
            0:{
                items:2
            },
            768:{
                items:2
            },
            992:{
                items:2
            }
        }
      });

      // Logo Slider (autoplay)
      $(".js_logo-slider_autoplay_3").owlCarousel({
        autoplay:true,
        autoplayTimeout:5000,
        autoplayHoverPause:true,
        loop:true,
        margin:10,
        nav:false,
        dots:false,
        responsive:{
            0:{
                items:2
            },
            768:{
                items:3
            },
            992:{
                items:2
            },
            1200:{
                items:3
            }
        }
      });

      // Pricing Slider
      $(".js_pricing-slider").owlCarousel({
        loop:true,
        margin:10,
        nav:true,
        dots:true,
        responsive:{
            0:{
                items:1
            },
            768:{
                items:2
            },
            992:{
                items:2
            },
            1200:{
                items:3
            }
        },
        navText : ["<span class='dotted-link2'><i class='fa fa-chevron-left'></i> <span>Prev</span></span>","<span class='dotted-link2'><span>Next</span> <i class='fa fa-chevron-right'></i></span>"]
      });

      // Testimonials Slider
      $(".js_testi-slider").owlCarousel({
        loop:true,
        margin:10,
        nav:true,
        dots:false,
        responsive:{
          0:{
              items:1
          },
          768:{
              items:1
          },
          992:{
              items:1
          }
        },
        navText: [ "<span class='link-circle'><i class='fa fa-angle-left'></i></span>","<span class='link-circle'><i class='fa fa-angle-right'></i></span>" ]
      });

      // Testimonials Slider
      $(".js_testi-slider_autoplay").owlCarousel({
        autoplay:true,
        autoplayTimeout:5000,
        autoplayHoverPause:true,
        loop:true,
        margin:10,
        nav:true,
        dots:false,
        responsive:{
          0:{
              items:1
          },
          768:{
              items:1
          },
          992:{
              items:1
          }
        },
        navText: [ "<span class='link-circle'><i class='fa fa-angle-left'></i></span>","<span class='link-circle'><i class='fa fa-angle-right'></i></span>" ]
      });

      // Content Slider
      $(".js_vertical-slider").owlCarousel({
        loop:false,
        margin:10,
        nav:false,
        dots:true,
        responsive:{
          0:{
              items:1
          },
          768:{
              items:2
          },
          992:{
              items:1
          }
        }
      });


      // Content Slider (autoplay)
      $(".js_vertical-slider_autoplay").owlCarousel({
        autoplay:true,
        autoplayTimeout:5000,
        autoplayHoverPause:true,
        loop:false,
        margin:10,
        nav:false,
        dots:true,
        responsive:{
          0:{
              items:1
          },
          768:{
              items:2
          },
          992:{
              items:1
          }
        }
      });

    },


    rangeSlider: function(){

      $("#slider-limit").noUiSlider({
        start: [ 20, 80 ],
        behaviour: 'drag',
        connect: true,
        range: {
          'min': 0,
          'max': 120
        }
      });

      $("#slider-limit").Link('lower').to( $('#slider-limit-value-min') )
      $("#slider-limit").Link('upper').to( $('#slider-limit-value-max') );

    },


    tooltipScript: function(){

      $('[data-toggle="tooltip"]').tooltip();

    },


    customSelect: function(){

      $('.selectpicker').selectpicker({
        iconBase: 'fa',
        tickIcon: 'fa-check',
        size: 4
      });

    },

    socialLinksTrigger: function(){

      // Social
      $('.entry-social-trigger').on('click', function () {
        $(this).next("ul").toggleClass('animated bounceIn');
      })

    },

    loadingButton: function(){

      // Loading
      $('#loading-btn').on('click', function () {
        $(this).find(".fa").toggleClass('fa-spin');
        $(this).button('toggle'); // change 'toggle' with 'loading'
      })

    },

    filterButton: function(){

      // Filter Trigger
      $('#filterWrapper').on('shown.bs.collapse', function () {
        $('#filterTrigger').html('<i class="fa fa-toggle-on"></i><span>Close Options</span>');
      });

      $('#filterWrapper').on('hidden.bs.collapse', function () {
        $('#filterTrigger').html('<i class="fa fa-toggle-off"></i><span>Open Options</span>');
      });

    },

    galleryFilter: function(){

      // Gallery Filter Trigger
      $("#galleryFilterTrigger").toggle(function() {
        $(this).find(".fa").removeClass("fa-toggle-off").addClass("fa-toggle-on");
        $("#gallerySidebar").addClass("gallery-sidebar__is-visible");
        $("#galleryContent").addClass("gallery-sidebar__is-visible");
      }, function () {
        $(this).find(".fa").removeClass("fa-toggle-on").addClass("fa-toggle-off");
        $("#gallerySidebar").removeClass("gallery-sidebar__is-visible");
        $("#galleryContent").removeClass("gallery-sidebar__is-visible");
      });

    },

    scrollNav: function(){

      $(".scroll-local").localScroll({
        target: "body",
        duration: 1500,
        offset: 0,
        easing: "easeInOutExpo"
      });

      var section    = $(".page-section, .top-wrapper");
      var menu_item  = $(".navbar-nav.scroll-local li");

      $(window).scroll(function() {
        section.filter(":in-viewport:first").each(function() {
          var active_section = $(this);
          var active_link    = $('.navbar-nav.scroll-local li a[href="#' + active_section.attr("id") + '"]');
          menu_item.removeClass("active");
          active_link.parent().addClass("active");
        });

      });

    },


    stickyHeader: function(){

      $('.header__fixed').affix({
        offset: {
          top: 10
        }
      });

      // add top padding for the Top Wrapper depends on Top Bar and Header height
      var bar_height = $('.h-top-bar').outerHeight(),
          header_height = $('.header-main').outerHeight(),
          header_pad = bar_height + header_height * 2;

      $('.top-wrapper').css('padding-top', header_pad);

    },


    GMapAddress: function(){

      // Google Map close/open button
      $('#gmapTrigger').click(function() {
        if ( $("#gmapWrapper").hasClass('in') ) {
          $(this).text('Open Google Map');
        } else {
          $(this).text('Close Google Map');
        }
      });

      $('#map_canvas').gmap3({
        marker:{
          address: '40.719939, -74.010579' 
        },
        map:{
          options:{
            zoom: 12,
            scrollwheel: false,
            streetViewControl : true,
            styles: [{
                "featureType": "water",
                "elementType": "geometry.fill",
                "stylers": [{
                    "color": "#ededed"
                }
                ]
            }, {
                "featureType": "transit",
                "stylers": [{
                    "color": "#808080"
                }, {
                    "visibility": "off"
                }
                ]
            }, {
                "featureType": "road.highway",
                "elementType": "geometry.stroke",
                "stylers": [{
                    "visibility": "on"
                }, {
                    "color": "#ffffff"
                }
                ]
            }, {
                "featureType": "road.highway",
                "elementType": "geometry.fill",
                "stylers": [{
                    "color": "#ffffff"
                }
                ]
            }, {
                "featureType": "road.local",
                "elementType": "geometry.fill",
                "stylers": [{
                    "visibility": "on"
                }, {
                    "color": "#f7f7f7"
                }, {
                    "weight": 1.8
                }
                ]
            }, {
                "featureType": "road.local",
                "elementType": "geometry.stroke",
                "stylers": [{
                    "color": "#ffffff"
                }
                ]
            }, {
                "featureType": "poi",
                "elementType": "geometry.fill",
                "stylers": [{
                    "visibility": "on"
                }, {
                    "color": "#ebebeb"
                }
                ]
            }, {
                "featureType": "administrative",
                "elementType": "geometry",
                "stylers": [{
                    "color": "#ffffff"
                }
                ]
            }, {
                "featureType": "road.arterial",
                "elementType": "geometry.fill",
                "stylers": [{
                    "color": "#ffffff"
                }
                ]
            }, {
                "featureType": "landscape",
                "elementType": "geometry.fill",
                "stylers": [{
                    "visibility": "on"
                }, {
                    "color": "#f7f7f7"
                }
                ]
            }, {
                "featureType": "road",
                "elementType": "labels.text.fill",
                "stylers": [{
                    "color": "#858585"
                }
                ]
            }, {
                "featureType": "administrative",
                "elementType": "labels.text.fill",
                "stylers": [{
                    "visibility": "on"
                }, {
                    "color": "#858585"
                }
                ]
            }, {
                "featureType": "poi",
                "elementType": "labels.icon",
                "stylers": [{
                    "visibility": "off"
                }
                ]
            }, {
                "featureType": "poi",
                "elementType": "labels",
                "stylers": [{
                    "visibility": "off"
                }
                ]
            }, {
                "featureType": "road.arterial",
                "elementType": "geometry.stroke",
                "stylers": [{
                    "color": "#ffffff"
                }
                ]
            }, {
                "featureType": "road",
                "elementType": "labels.icon",
                "stylers": [{
                    "visibility": "off"
                }
                ]
            }, {}, {
                "featureType": "poi",
                "elementType": "geometry.fill",
                "stylers": [{
                    "color": "#f9f9f9"
                }
                ]
            }
          ]
          }
        }
     });
    }

  };


  $(document).ready(function() {
    Core.initialize(); 
  });
  

})(jQuery);