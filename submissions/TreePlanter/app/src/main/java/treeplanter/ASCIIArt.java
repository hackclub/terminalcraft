package treeplanter;

import java.io.IOException;
import java.io.InputStream;

public class ASCIIArt {

    static String hike;
    static String tree;

    ASCIIArt() {
        try {
            InputStream is = getClass().getClassLoader().getResourceAsStream("hike.txt");
            hike = new String(is.readAllBytes());
            is = getClass().getClassLoader().getResourceAsStream("tree.txt");
            tree = new String(is.readAllBytes());
        } catch (IOException e) {
            e.fillInStackTrace();
        }
    }

    public static String getHike() {
        return hike;
    }

    public static String getTree() {
        return tree;
    }

}
