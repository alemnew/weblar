
import java.awt.GraphicsConfiguration;
import java.awt.GraphicsEnvironment;
import java.awt.Rectangle;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintStream;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import org.monte.media.Format;
import org.monte.media.FormatKeys;
import org.monte.media.VideoFormatKeys;
import org.monte.media.math.Rational;
import org.monte.screenrecorder.ScreenRecorder;
import org.openqa.selenium.Dimension;
import org.openqa.selenium.TimeoutException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

import org.openqa.selenium.logging.LogType;
import org.openqa.selenium.logging.LoggingPreferences;
import org.openqa.selenium.remote.CapabilityType;
import org.openqa.selenium.JavascriptExecutor;

public class CaptureScreen {

    private ScreenRecorder screenRecorder;

    public CaptureScreen() {
    }

    public static void main(String[] args)
            throws IOException, InterruptedException, Exception {

        String url = args[0]; //"http://www.aalto.fi/en/";
        String videoFileName = args[1]; //"aalto-test"; //

        System.setProperty(
                "webdriver.chrome.driver", System.getProperty("user.home") + "/chromedriver");
        int width = 0;
        int height = 0;
        long startTime = 0L;
        //long finishTime = 0L;
        //long sleepTime = 0L;

        try {
            LoggingPreferences logPrefs = new LoggingPreferences();
            logPrefs.enable(LogType.PERFORMANCE, Level.ALL);
            ChromeOptions chromeoptions = new ChromeOptions();

            //chromeoptions.addArguments("--headless");
            /*String downloadFilepath = "/tmp";
            HashMap<String, Object> chromePrefs = new HashMap<String, Object>();
            chromePrefs.put("profile.default_content_settings.popups", 0);
            chromePrefs.put("download.default_directory", downloadFilepath);
             */
            //chromeoptions.addArguments("--no-sandbox");
            chromeoptions.addArguments("-disable-quic");
            //chromeoptions.addArguments("start-maximized");
            chromeoptions.addArguments("disable-infobars");
            chromeoptions.addArguments("-incognito");
            chromeoptions.addArguments("--disable-extensions");
            chromeoptions.addArguments("--disable-browser-side-navigation");

            chromeoptions.setCapability(CapabilityType.LOGGING_PREFS, logPrefs);

            WebDriver driver = new ChromeDriver(chromeoptions);
            Dimension dmnsn = new Dimension(1366, 768);
            driver.manage().window().setSize(dmnsn);
            driver.manage().deleteAllCookies();

            CaptureScreen videoRecord = new CaptureScreen();
            height = driver.manage().window().getSize().getHeight();
            width = driver.manage().window().getSize().getWidth();
            try {
                driver.manage().timeouts().implicitlyWait(2000, TimeUnit.MILLISECONDS); 
                driver.manage().timeouts().pageLoadTimeout(60, TimeUnit.SECONDS);
                driver.manage().timeouts().setScriptTimeout(60, TimeUnit.SECONDS);
                startTime = System.currentTimeMillis();
                videoRecord.startRecording(videoFileName, width, height);
                driver.get(url);  
                
            } catch (TimeoutException toe) {
                System.err.println("ERR:- !Timeout exception ocurred: " 
                        + toe.getMessage() + "\nThe session is closing ");
                videoRecord.stopRecording();
                videoRecord.removeVideo(videoFileName);
                driver.close();
                driver.quit();
                System.exit(0);
            } catch (Exception ex) {
                System.err.println("ERR:- !Exception ocurred:: " 
                        + ex.getMessage() + "\n!The session is closing ");
                //videoRecord.writeLog(ex.getMessage() + " --> " + url);
                videoRecord.stopRecording();
                videoRecord.removeVideo(videoFileName);
                driver.close();
                driver.quit();
                System.exit(0);
            }

            long finishTime = System.currentTimeMillis();
            long totalTime = finishTime - startTime;

            long sleepTime = 35000L - totalTime;
            try {
                if (sleepTime > 0L) {
                    Thread.sleep(sleepTime);
                    videoRecord.stopRecording();
                }
            } catch (InterruptedException ex) {
                Thread.currentThread().interrupt();
            }            

            /*PrintStream routp;
            // write the start time of the rendering
            routp = new PrintStream(new FileOutputStream(
                    videoFileName + "_ren_start.json"));
            routp.print("{\"rend_start\":" + startTime + "}");
            routp.close(); 
            */
            /**
             * Get the timing information using JavaSctipt Executor and and the
             * window.performance.timing API
             *
             * source: https://community.akamai.com/community/web-performance/blog/2016/08/25/using-navigation-timing-apis-to-understand-your-webpage 
             */
            JavascriptExecutor js = ((JavascriptExecutor) driver);
            String atffilename =  "atfindex.js";
            //System.out.println(atffilename);
            Util util = new Util();
            String atfindexjs = util.readWebPerfJSFile(atffilename);
            //System.out.println(atfindexjs);
            Object atf = null;
            try {
                atf = js.executeScript(atfindexjs);
                System.out.println(atf);
            } catch (Exception ex) {
                System.err.println("ERR:- ERROR JS execution: " 
                        + ex.getMessage() + "\nThe session is closing ");
                //videoRecord.stopRecording();
                videoRecord.removeVideo(videoFileName);
                driver.close();
                driver.quit();
                System.exit(0);
                
            }
            
            if (atf != null) {
                PrintStream outp;
                //write the ATF value 
                outp = new PrintStream(new FileOutputStream(
                        videoFileName + "_atf.json"));
                outp.print(atf.toString().replace("{", "{\"").replace("=", "\"=")
                        .replace(", ", ", \"").replace("=", ":"));
                outp.close();
                
            }
            else{ 
                System.err.println("There is an error in the A-T-F. ");
            }
            driver.close();
            driver.quit();
        } catch (Exception ex) {
            System.err.println("!!!Exception ocurred: " + ex.getMessage());
        }

        if (!new File("resolution").exists()) {
            try {
                PrintStream outps;
                outps = new PrintStream(new FileOutputStream(
                        "resolution"));
                outps.print(String.valueOf(width) + "x" + String.valueOf(height));
                outps.close();
            } catch (IOException io) {
                System.err.println("IO Error" + io.getMessage());
            }
        }

        System.exit(0);
    }

    public void removeVideo(String videoFileName) {
        File f = new File(videoFileName + ".avi");
        if (f.exists() && !f.isDirectory()) {
            f.delete();
        }
    }
    public void startRecording(String videoFileName, int width, int height)
            throws Exception {
        String workingDir = System.getProperty("user.dir") + "/";
        File file = new File(workingDir);

        Rectangle captureSize = new Rectangle(0, 0, width, height);

        GraphicsConfiguration gc
                = GraphicsEnvironment.getLocalGraphicsEnvironment().getDefaultScreenDevice()
                        .getDefaultConfiguration();

        screenRecorder = new SpecializedScreenRecorder(
                gc,
                captureSize,
                new Format(new Object[]{FormatKeys.MediaTypeKey, FormatKeys.MediaType.FILE, FormatKeys.MimeTypeKey, "video/avi"}),
                new Format(new Object[]{FormatKeys.MediaTypeKey, FormatKeys.MediaType.VIDEO, FormatKeys.EncodingKey,
            "tscc",
            VideoFormatKeys.CompressorNameKey,
            "tscc", VideoFormatKeys.DepthKey, Integer.valueOf(24),
            FormatKeys.FrameRateKey, Rational.valueOf(20.0D), VideoFormatKeys.QualityKey, Float.valueOf(1.0F),
            FormatKeys.KeyFrameIntervalKey, Integer.valueOf(1200)}), new Format(new Object[]{FormatKeys.MediaTypeKey,
            FormatKeys.MediaType.VIDEO, FormatKeys.EncodingKey, "black", FormatKeys.FrameRateKey,
            Rational.valueOf(10.0D)}), null, file, videoFileName);
        screenRecorder.start();
    }

    public void stopRecording() throws Exception {
        screenRecorder.stop();
    }

    public void writeLog(String msg) {
        try {
            String timeStamp = new SimpleDateFormat("yyyyMMdd_HH:mm:ss")
                    .format(Calendar.getInstance().getTime());

            FileWriter fw = new FileWriter("/tmp/renderingserver.log", true);
            fw.write(timeStamp + ": " + msg + "\n");
            fw.close();
        } catch (IOException io) {
            System.err.println("IO Error" + io.getMessage());
        }
    }
}
