package treeplanter;

import java.util.Arrays;
import java.util.HashMap;

public class TreeGenerators {

    public static HashMap<String, TreeGenerator> treeGenerators = new HashMap<String, TreeGenerator>();
    public static TreeGenerator[] treeGeneratorsSorted;
    static long treas;
    static long treesPlanted;
    static long treeGoal = 500000;
    static int multiplier = 1;

    TreeGenerators() {
        new TreeGenerator("student", "Student Volunteer", "I guess that free labor isn't free anymore `\\_(?_?)_/`", 5,
                1);
        new TreeGenerator("programmer", "Programmer",
                "\"I plant trees at O(log(n)) time)\" (This isn't true it's actually O(n), but no ones's smart enough to correct them)",
                500, 5);
        new TreeGenerator("farm", "Tree Farm",
                "Go and support those local farmers ... they really need it",
                1000, 50);
        new TreeGenerator("bank", "Bank",
                "The big banks don't fail!",
                10000, 100);

        treeGeneratorsSorted = new TreeGenerator[TreeGenerators.treeGenerators.size()];
        TreeGenerators.treeGenerators.values().toArray(treeGeneratorsSorted);
        Arrays.sort(treeGeneratorsSorted);
    }

    public static void activate2ndStage() {
        multiplier = -1;
        treeGoal *= (long) (treeGoal / 4.0);
    }

    public static long getTreeGoal() {
        return treeGoal;
    }

    public static void updateTreeValues() {
        for (TreeGenerator treeGenerator : treeGenerators.values()) {
            addTreas(treeGenerator.getTrees());
        }
    }

    public static void addTreas(long treas) {
        TreeGenerators.treas += treas;
        TreeGenerators.treesPlanted += multiplier * treas;
    }

    public static void removeTreas(long treas) {
        TreeGenerators.treas -= treas;
    }

    public static int getTotalTreesGeneratedPerSecond() {
        int perSecValue = 0;
        for (TreeGenerator treeGenerator : treeGenerators.values()) {
            perSecValue += multiplier * treeGenerator.getTreesGeneratedPerSecond();
        }

        return perSecValue;
    }
}
