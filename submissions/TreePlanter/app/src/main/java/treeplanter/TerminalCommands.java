package treeplanter;

import java.util.HashMap;

public class TerminalCommands {
    public static HashMap<String, Command> terminalCommands = new HashMap<>();

    public TerminalCommands() {
        new Help();
        new Status();
        new Plant();
        new Hire();
        new Shop();
        new Clear();
    }

    public static class Help extends Command {
        @Override
        public void action(String[] args) {
            System.out.println("How to call a command:");
            System.out.println("\t<command-name> (param1, param2, ... paramN)");
            if (args[0].isEmpty()) {
                System.out.println("Commands:");
                for (Command command : terminalCommands.values()) {
                    System.out.println("\t" + command);
                }
            } else {
                Command command = terminalCommands.get(args[0]);
                if (command == null)
                    System.out.println("That's not a command");
                else
                    System.out.println(terminalCommands.get(args[0]));
            }
        }

        @Override
        public String getID() {
            return "help";
        }

        @Override
        public String toString() {
            return UI.BOLD + "help" + UI.BOLDOFF + " - shows what you can do";
        }
    }

    public static class Status extends Command {

        @Override
        public void action(String[] args) {
            System.out.println("Treas Owned: " + TreeGenerators.treas + "      Trees Planted: "
                    + TreeGenerators.treesPlanted + "\n" +
                    "Total Trees Planted Per Second: " + TreeGenerators.getTotalTreesGeneratedPerSecond() + "\n" +
                    "Trees planted goal: " + TreeGenerators.getTreeGoal());
        }

        @Override
        public String getID() {
            return "status";
        }

        @Override
        public String toString() {
            return UI.BOLD + "status" + UI.BOLDOFF + " - shows your current status";
        }
    }

    public static class Plant extends Command {
        @Override
        public void action(String[] args) {
            TreeGenerators.addTreas(1);
        }

        @Override
        public String getID() {
            return "plant";
        }

        @Override
        public String toString() {
            return UI.BOLD + "plant" + UI.BOLDOFF + " - you'll plant one tree giving you one trea";
        }
    }

    public static class Hire extends Command {

        @Override
        public void action(String[] args) {
            // Checking for valid parameters
            if (args.length != 2) {
                System.out.println("Error: you have the wrong number of arguments");
                return;
            }
            TreeGenerator treeGenerator = TreeGenerators.treeGenerators.get(args[0]);
            int amountBought;

            if (treeGenerator == null) {
                System.out.println("That's not something you can buy");
                return;
            }
            try {
                amountBought = Integer.parseInt(args[1]);
                if (amountBought < 1) {
                    System.out.println("You can't hire that much");
                    return;
                }
            } catch (NumberFormatException e) {
                System.out.println("That's not a number");
                return;
            }
            int cost = treeGenerator.getNextNUnitsCost(amountBought);
            if (cost > TreeGenerators.treas) {
                System.out.println("You don't have enough treas");
                return;
            }

            treeGenerator.buy(amountBought);
            TreeGenerators.removeTreas(cost);
        }

        @Override
        public String getID() {
            return "hire";
        }

        @Override
        public String toString() {
            return UI.BOLD + "hire" + UI.BOLDOFF + " <shop ID> <integer> - hires workers to help your cause";
        }
    }

    public static class Shop extends Command {
        @Override
        public void action(String[] args) {
            int amountLookingFor;
            if (args[0].isEmpty()) {
                amountLookingFor = 1;
            } else {
                try {
                    amountLookingFor = Integer.parseInt(args[0]);
                    if (amountLookingFor < 1) {
                        System.out.println("Ummm, why are you looking to buy " + amountLookingFor);
                        return;
                    }
                } catch (NumberFormatException e) {
                    System.out.println("That's not a number");
                    return;
                }
            }

            for (TreeGenerator treeGenerator : TreeGenerators.treeGeneratorsSorted) {
                System.out.println(treeGenerator.getDescription(amountLookingFor) + "\n");
            }
        }

        @Override
        public String getID() {
            return "shop";
        }

        @Override
        public String toString() {
            return UI.BOLD + "shop <amount-looking-to-buy>" + UI.BOLDOFF + " - displays the shop";
        }
    }

    public static class Clear extends Command {
        @Override
        public void action(String[] args) {
            UI.clearConsole();
        }

        @Override
        public String getID() {
            return "clear";
        }

        @Override
        public String toString() {
            return UI.BOLD + "clear" + UI.BOLDOFF + " - clears the console of any text";
        }

    }

}
