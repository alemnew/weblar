
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
/**
 *
 * @author asresea1
 */
public class Util {

    // read the content of the JS file 
    public String readWebPerfJSFile(String filePath) {
        try {
            BufferedReader br = new BufferedReader(new FileReader(filePath));
            StringBuffer str = new StringBuffer();
            String line = br.readLine();
            while (line != null) {
                str.append(line);
                str.append("\n");
                line = br.readLine();
            }

            return str.toString();
        } catch (IOException e) {
            System.out.println(e.getMessage());
            return null;
        }
    }
}