package treeplanter;

import java.io.IOException;
import java.util.Scanner;
import java.util.concurrent.TimeUnit;
import static treeplanter.TerminalCommands.terminalCommands;

public class UI {

    public static final String BOLD = "\033[0;1m";
    public static final String BOLDOFF = "\033[0;0m";

    public static void startGame() {
        Scanner scanner = new Scanner(System.in);

        introduction(scanner);

        while (TreeGenerators.treesPlanted < TreeGenerators.getTreeGoal()) {
            invokeCommand(scanner.nextLine());
        }

        midway(scanner);
        TreeGenerators.activate2ndStage();

        while (TreeGenerators.treesPlanted > TreeGenerators.getTreeGoal()) {
            invokeCommand(scanner.nextLine());
        }

        ending(scanner);

        scanner.close();
    }

    private static void introduction(Scanner scanner) {
        typeOutMessageln("After finishing one of your projects you decide it's time to go outside");
        clearAfterUserInput(scanner);

        fillInMessage(ASCIIArt.getHike(), TimeUnit.MILLISECONDS, 2);
        System.out.println();
        typeOutMessageln("You climb and scale the closest mountain to you, finding a cherry blossom tree atop it");
        clearAfterUserInput(scanner);

        fillInMessage(ASCIIArt.getTree(), TimeUnit.MICROSECONDS, 100);
        System.out.println();
        typeOutMessageln("Hello my child, I see great potential within you.");
        typeOutMessageln("If you help me plant my children across the world, we can stop climate change.");
        clearAfterUserInput(scanner);

        typeOutMessageln(
                "So to you, I will offer on trea for every tree that you plant, that way you can afford to do this.");
        typeOutMessageln("Get started! you can plant a tree right now.");
        System.out.println();
        typeOutMessageln("(type \"plant\" to plant one tree)");

        while (true) {
            String str = scanner.nextLine();
            if (str.contains("plant")) {
                invokeCommand("plant");
                break;
            } else {
                typeOutMessageln("Come on! try planting a tree.");
            }
        }

        typeOutMessageln("Nice job. Take a look at what you have.");
        invokeCommand("status");
        typeOutMessageln("See look, you have one trea, which you can use to hire people to your cause");
        typeOutMessageln("Over to the right you the number of trees you've planted in total");
        typeOutMessageln("Let's try getting to " + TreeGenerators.getTreeGoal() + " trees planted!");
        clearAfterUserInput(scanner);

        typeOutMessageln("(type \"help\" to view what else you can do)");
    }

    private static void midway(Scanner scanner) {
        typeOutMessageln("Hey");
        typeOutMessageln("HEY HEY HEY");
        clearAfterUserInput(scanner);
        typeOutMessageln("After reaching your goal, you realize that the world is worse off than it was");
        typeOutMessageln("Sea levels have risen 100% quicker than before ...");
        typeOutMessageln("There have been more fires than ever");
        typeOutMessageln("And the elderly are suffering; they barely breath anymore");
        typeOutMessageln("You realize that planting trees, especially only the same type of tree was a fatal mistake");
        clearAfterUserInput(scanner);
        typeOutMessageln("But you can still correct your wrongs");
        typeOutMessageln("It's time to deroot your trees");
        typeOutMessageln("Not all of them though, maybe just three-fourths of them");
        clearAfterUserInput(scanner);
        System.out.println();
        typeOutMessageln("You got this!");
        typeOutMessageln("YOU GOT THIS!!!!");
    }

    private static void ending(Scanner scanner) {
        typeOutMessageln("Congrats!");
        typeOutMessageln("You did it");
        typeOutMessageln("Even if you simultaeneously destroyed and fixed the world");
        typeOutMessageln("I will commend your efforts");
        clearAfterUserInput(scanner);

        fillInMessage(ASCIIArt.tree, TimeUnit.MICROSECONDS, 50);
        System.out.println();
        typeOutMessageln("Thanks for playing! ^-^");
    }

    private static void typeOutMessageln(String messsage) {
        typeOutMessage(messsage, TimeUnit.MILLISECONDS, 50);
        System.out.println();
    }

    private static void invokeCommand(String str) {
        TreeGenerators.updateTreeValues();
        str = str.toLowerCase().trim().replaceAll("\\s+", " ") + " ";
        int index = str.indexOf(" ");
        try {
            terminalCommands.get(str.substring(0, index)).action(str.substring(index + 1).split(" "));
        } catch (NullPointerException e) {
            System.out.println("That's not a valid command");
        }
    }

    private static void typeOutMessage(String message, TimeUnit unit, long delay) {
        char[] charArray = message.toCharArray();

        try {
            for (int i = 0; i < charArray.length; i++) {
                int iMod = i % 2;
                if (iMod == 1)
                    System.out.print("\b");
                System.out.print(charArray[i]);
                if (iMod == 0)
                    System.out.print("_");
                unit.sleep(delay);
            }
            if (message.length() % 2 == 1) {
                System.out.print("\b "); // There's a space here otherwise \b won't work ¯\_(ツ)_/¯
            }
        } catch (Exception e) {
            e.fillInStackTrace();
        }
    }

    private static void fillInMessage(String message, TimeUnit unit, long delay) {
        char[] charArray = message.toCharArray();

        try {
            for (int i = 0; i < charArray.length; i++) {
                System.out.print(charArray[i]);
                unit.sleep(delay);
            }
        } catch (Exception e) {
            e.fillInStackTrace();
        }
    }

    private static void clearAfterUserInput(Scanner scanner) {
        try {
            while (System.in.available() > 0) {
                System.in.read(new byte[System.in.available()]);
            }
        } catch (IOException e) {
            e.fillInStackTrace();
        }
        System.out.println("(ENTER)");
        scanner.nextLine();
        clearConsole();
    }

    public static void clearConsole() {
        try {
            if (System.getProperty("os.name").contains("Windows")) {
                new ProcessBuilder("cmd", "/c", "cls").inheritIO().start().waitFor();
            } else {
                System.out.print("\033\143");
            }
        } catch (IOException | InterruptedException ex) {
            ex.fillInStackTrace();
        }
    }

}
