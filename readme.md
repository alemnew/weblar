
# Web Performance: in terms  Web Latency, ATF and Rendering Time
Measures the rendeirng time a website in a browser window. 

# Requirements 
- jre 1.8 
- chrome browser and chromedriver (it can work with other browser, with some workaround). 
- ImageMagic 
- FFMpeg 

** Install in the docker container using the docker script. 

# Name 
WebLAR 
[src](src/) contains java source files for recording screen based on selenium framework. 

# How to calculate the metrics 
- dom = t.domContentLoadedEventEnd - t.navigationStart;
- tcpConct = t.connectEnd - t.connectStart;
- dnsLookup = t.domainLookupEnd - t.domainLookupStart;
- ttfb = t.responseStart -  t.navigationStart;
- pltStart = t.loadEventStart - t.navigationStart;
- pltUserTime = t.loadEventEnd -  t.navigationStart;
- requestTime = t.responseEnd - t.requestStart;
- fetchTime = t.responseEnd -t.fetchStart;
- serverResponseTime = t.responseStart - t.requestStart;

[Source: Akamai web performance blog](https://community.akamai.com/community/web-performance/blog/2016/08/25/using-navigation-timing-apis-to-understand-your-webpage)

# Known Issues 

The experiment may fails because of 'Time out error that may occur while loading
the pages'. The problem looks a bug with chromedriver/selenium, but this doesn't
affect the result of the experiment. 

The issue has been reported by other users as well [in stackoverfllow](https://sqa.stackexchange.com/questions/9007/how-to-handle-time-out-receiving-message-from-the-renderer-in-chrome-driver)
