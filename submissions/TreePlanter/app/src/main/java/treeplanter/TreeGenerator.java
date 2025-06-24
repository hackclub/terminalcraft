package treeplanter;

public class TreeGenerator implements Comparable<TreeGenerator> {

    private String id;
    private String name;
    private String descrip;
    private long lastTime;
    private int unitsOwned = 0;
    private int baseCost;
    private double priceRateIncrease = 1.15;
    private double multiplier = 1;
    private int treesPerSecondPerUnit;

    public TreeGenerator(String id, String name, String description, int baseCost, int treesPerSecondPerUnit) {
        lastTime = System.currentTimeMillis();
        this.id = id;
        this.name = name;
        this.descrip = description;
        this.baseCost = baseCost;
        this.treesPerSecondPerUnit = treesPerSecondPerUnit;
        TreeGenerators.treeGenerators.put(id, this);
    }

    public long getTrees() {
        long currentTime = System.currentTimeMillis();
        double seconds = (currentTime - lastTime) / 1000.0;
        long roundedSeconds = (long) seconds;

        if (seconds > roundedSeconds)
            lastTime = currentTime - (long) ((seconds - roundedSeconds) * 1000);

        return calculateTrees(roundedSeconds);
    }

    private long calculateTrees(long seconds) {
        return (long) (seconds * getTreesGeneratedPerSecond());
    }

    public void addMultiplier(double multiplier) {
        this.multiplier *= multiplier;
    }

    public int getNextNUnitsCost(int n) {
        n -= 1;
        if (n < 0) {
            throw new IllegalArgumentException("n < 1");
        }

        double totalCostToNow = baseCost
                * ((Math.pow(priceRateIncrease, (unitsOwned - 1) + 1) - 1) / (priceRateIncrease - 1));
        double totalNextCost = baseCost
                * ((Math.pow(priceRateIncrease, (unitsOwned + n) + 1) - 1) / (priceRateIncrease - 1));

        double cost = totalNextCost - totalCostToNow;

        return (int) cost;
    }

    public int getTreesGeneratedPerSecond() {
        return (int) (treesPerSecondPerUnit * unitsOwned * multiplier);
    }

    public void buy(int n) {
        unitsOwned += n;
    }

    @Override
    public String toString() {
        return getDescription(1);
    }

    public String getDescription(int amountLookingToBuy) {
        return UI.BOLD + name + UI.BOLDOFF + "     ID: " + id + "\n" +
                "   Your " + name.toLowerCase() + "s plant " + UI.BOLD + (calculateTrees(1)) + UI.BOLDOFF
                + " trees per second\n" +
                "   Each " + name.toLowerCase() + " plants " + UI.BOLD + (treesPerSecondPerUnit * multiplier)
                + UI.BOLDOFF
                + " trees per second\n"
                +
                "   Number Owned: " + unitsOwned + "     Cost: " + getNextNUnitsCost(amountLookingToBuy) + " treas"
                + "\n" +
                "   " + descrip;
    }

    @Override
    public int compareTo(TreeGenerator o) {
        return this.baseCost - o.baseCost;
    }
}
