class Program
{
 public int rawr = 1;
public int[] picked = new int[0];
public int score = 0;
public int streak = 0;
Random rnd = new Random();
public int qNum = 0;
public string? cAns;
public bool trues = false;
public int longestStreak = 0;
static void Main()
{
    Program game = new Program();
    game.runGame();
    while(true)
    {
        string? input = Console.ReadLine();
        if(string.IsNullOrEmpty(input))
        {
            break;
        }else
        {
            game.checkAnswer(input);
        }
    }
}
public void runGame()
{
    if(longestStreak < streak)
    {
        longestStreak = streak;
    }
    trues = false;
    qNum = rnd.Next(1, 30);
    for(int i = 0; i < picked.Length; i++)
    {
        if(qNum == picked[i])
        {
        runGame();
        trues = true;
        break;
        }
    }
    if(!trues)
    {
        Console.WriteLine(questionFinder(qNum));
        Array.Resize(ref picked, picked.Length + 1);
        picked[picked.Length - 1] = qNum;
        trues = false;
    }
    if(picked.Length >= 20)
    {
        endGame();
    }
    
}
public void endGame()
{
    Console.WriteLine("Thank you for doing the yugioh quiz! your final score was: " + score + " and your longest streak was " + longestStreak);
}
public string questionFinder(int num)
{
    switch(num)
    {
        case 1: 
            cAns = "C";
            return "How much attack does Blue-Eyes White Dragon have? \n" + "(A). 2,500 \n" + "(B). 2,000 \n" + "(C). 3,000 \n" + "(D). 3,500";
        case 2:
            cAns = "A";
            return "How much defence does Blue-Eyes White Dragon have? \n" + "(A). 2,500 \n" + "(B). 2,000 \n" + "(C). 3,000 \n" + "(D). 3,500";
        case 3:
            cAns = "A";
            return "How much attack does Dark Magician have? \n" + "(A). 2,500 \n" + "(B). 2,000 \n" + "(C). 3,000 \n" + "(D). 3,500";
        case 4:
            cAns = "B";
            return "As of March 2025, how many cards are in the mulcharmy archetype? \n" + "(A). 2 \n" + "(B). 3 \n" + "(C). 10 \n" + "(D). 23";
        case 5:
            cAns = "D";
            return "Which of these Yu-Gi-Oh sets is the oldest? \n" + "(A). Supreme Darkness \n" + "(B). The Infinite Forbidden \n" + "(C). Duels of the Deep \n" + "(D). Metal Raiders";
        case 6:
            cAns = "A";
            return "Which of these summoning mechanics is the newest? \n" + "(A). Link Summoning \n" + "(B). Synchro Summoning \n" + "(C). Fusion Summoning \n" + "(D). XYZ Summoning";
        case 7:
            cAns = "B";
            return "Which card of these is banned? \n" + "(A). Harpie's Feather Duster \n" + "(B). Graceful Charity \n" + "(C). Pot of Desires \n" + "(D). Mirror Force";
        case 8:
            cAns = "A";
            return "What is an FTK in Yugioh? \n" + "(A). First Turn Kill \n" + "(B). Final Tier Kill \n" + "(C). Finish Time Kwick \n" + "(D). First To Kickbox";
        case 9:
            cAns = "C";
            return "What does OCG stand for? \n" + "(A). Organized Card Game \n" + "(B). Organic Card Game \n" + "(C). Original Card Game \n" + "(D). Open Card Game";
        case 10:
            cAns = "B";
            return "What is the largest open entry Yugioh tournament \n" + "(A). OTS \n" + "(B). YCS \n" + "(C). WCQ \n" + "(D). Worlds";
        case 11:
            cAns = "C";
            return "What does OTS mean \n" + "(A). Official Trade Store \n" + "(B). Original Trade Store \n" + "(C). Official Tournament Store \n" + "(D). Open Tournament Scene";
        case 12:
            cAns = "D";
            return "Which of these is the highest rarity \n" + "(A). Super Rare \n" + "(B). Ultra Rare \n" + "(C). Secret Rare \n" + "(D). Collectors Rare";
        case 13:
            cAns = "A";
            return "Droll & __________ bird? \n" + "(A). Lock \n" + "(B). Flame \n" + "(C). Giant \n" + "(D). Black";
        case 14:
            cAns = "C";
            return "Which of these cards is a spell \n" + "(A). Anti-Spell Fragrance \n" + "(B). Skill Drain \n" + "(C). Mystical Space Typhoon \n" + "(D). Spell Reclamation";
        case 15:
            cAns = "A";
            return "What is the Minimum Number of Cards in a yugioh Deck\n" + "(A). 40  \n" + "(B). 50 \n" + "(C). 60 \n" + "(D). No Minimum";
        case 16:
            cAns = "D";
            return "Which of these are not a format\n" + "(A). TCG \n" + "(B). OCG \n" + "(C). Asian English \n" + "(D). Traditional";
        case 17:
            cAns = "B";
            return "What day of the week do new yugioh cards release on \n" + "(A). Thursday \n" + "(B). Friday \n" + "(C). Saturday \n" + "(D). Sunday";
        case 18:
            cAns = "A";
            return "What symbol indicates that the text before was the cost of the card. \n" + "(A). ; \n" + "(B). : \n" + "(C). , \n" + "(D). / ";
        case 19:
            cAns = "D";
            return "Can you play cards in other languages in the USA other than English? \n" + "(A). No \n" + "(B). Yes, if you have an English copy for translation \n" + "(C). Yes, if the opponent agrees \n" + "(D). Yes, if it is not an Asian language";
        case 20:
            cAns = "C";
            return "What is the time limit for a round of yugioh? \n" + "(A). One Hour \n" + "(B). 50 Minutes \n" + "(C). 45 Minutes \n" + "(D). No Limit";
        case 21:
            cAns = "A";
            return "What is the most annoying deck\n" + "(A). Maliss \n" + "(B). Anything Fiendsmith \n" + "(C). Tenpai \n" + "(D). Voiceless Voice";
        case 22:
            cAns = "B";
            return "What is the term for a bad hand in yugioh \n" + "(A). A fumble \n" + "(B). A Brick \n" + "(C). There is no term \n" + "(D). A Bundt ";
        case 23:
            cAns = "C";
            return "What is the effect of Pot of Greed \n" + "(A). Draw 3 cards \n" + "(B). Draw 2 cards, then discard one card \n" + "(C). Draw 2 cards \n" + "(D). Draw 4 cards";
        case 24:
            cAns = "C";
            return "What card lets you send cards from the top of your deck to the graveyard until your deck has the same number of cards as your opponent \n" + "(A). Deck Burn \n" + "(B). Evenly Matched \n" + "(C). That Grass Looks Greener \n" + "(D). Let's Even the Playingfield";
        case 25:
            cAns = "B";
            return "What is the highest level in yugioh? \n" + "(A). 13 \n" + "(B). 12 \n" + "(C). 10 \n" + "(D). 8";
        case 26:
            cAns = "A";
            return "How many points do you get for winning a round of Yugioh \n" + "(A). 3 \n" + "(B). 1 \n" + "(C). 5 \n" + "(D). 2";
        case 27:
            cAns = "C";
            return "What is the effect of Raigeki \n" + "(A). Destroy all spells and traps on the field \n" + "(B). Destroy all monsters on the field \n" + "(C). Destroy all of your opponents monsters \n" + "(D). Destroy all of your opponents spells and traps";
        case 28:
            cAns = "B";
            return "What is the effect of Dark Hole \n" + "(A). Destroy all spells and traps on the field \n" + "(B). Destroy all monsters on the field \n" + "(C). Destroy all of your opponents monsters \n" + "(D). Destroy all of your opponents spells and traps";
        case 29:
            cAns = "C";
            return "What is the effect of Harpie's feather Duster \n" + "(A). Destroy all spells and traps on the field \n" + "(B). Destroy all monsters on the field \n" + "(C). Destroy all of your opponents monsters \n" + "(D). Destroy all of your opponents spells and traps";
        case 30:
            cAns = "A";
            return "What is the summoning requirements for Blue-Eyes ultimate dragon \n" + "(A). 3 Blue-Eyes white dragons \n" + "(B). 2 Blue-Eyes White Dragons \n" + "(C). 1 Blue-Eyes white Dragon and 4 monsters \n" + "(D). 3 Blue-Eyes White Dragons and 2 monsters";
        default:
            return "Invalid question number.";
    }
}
private void checkAnswer(string ans)
{
    if(ans == cAns)
    {
        score++;
        streak++;
        Console.WriteLine("Correct!" + " Your Streak is: " + streak + " And your total score is: " + score);
    }else
    {
        streak = 0;
        Console.WriteLine("incorrect the correct answer was: " + cAns + " Your Streak is: " + streak + " And your total score is: " + score);
    }
    runGame();
}
}
