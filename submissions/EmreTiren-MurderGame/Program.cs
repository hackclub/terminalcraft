// Code: Text Adventure Game

namespace TextAdventure
{
    class Program
    {
        static void Main(string[] args)
        {
            // Start de game
            Game game = new Game();
            game.Start();
        }
    }

    class Game
    {
        private List<string> inventory = new List<string>(); // Dit is je inventory
        private List<string> notepad = new List<string>();  // Dit is je in-game notepad
        private List<string> gevondenClues = new List<string>(); // Dit zijn de gevonden aanwijzingen
        private bool clueDraakArm = false;
        private bool bloedigMes = false;
        private string partnerchoice1 = "";
        private bool Angela = false;
        private bool Jack = false;
        private bool Cam = false;
        private bool Zack = false;
        private string partner = "";

        public void Start()
        {
            // Begin bij de eerste scène
            Scene0();
            return;
        }

private void Scene0()
{
    Console.WriteLine("Welcome to this text adventure game!");
    Console.WriteLine("This story will be about a murder and You are Doctor Temprance Brennan and together with your friend and FBI agent Booth you will solve a murder!");
    Console.WriteLine("We recommend to use get a notepad and write your findings. But we will also give all the clues on a notepad for you in this console!!!");
    Console.WriteLine("Let's Start!");
    Console.ReadKey();
    Scene1();
    
}

    private void Scene1() //partner kiezen
    {
        Console.Clear();
        Console.WriteLine("You are in the Jeffersonian Institute, surrounded by the scent of old bone and preservatives.\n" +
                            "The sound of skeletons clicking against each other as they are moved fills the space.\n" +
                            "Agent Seeley Booth stands next to you, his face tense. He folds his arms and nods toward a table covered with bones.\n\n" +
                            "\"We have a problem,\" he says with a sigh. \"A body was found dead… here, among the other skeletons in a old ruin.\n" +
                            "As if he just belonged there.\"\n\n" +
                            "He points to a partially reconstructed skeleton, carefully laid out, but not all the bones are equally old.\n" +
                            "Among the ancient remains lies something newer—too new.\n\n" +
                            "\"This is not an excavation. This is a murder.\"");
Console.WriteLine("Who do you take with you?");
        Console.WriteLine("1. Angela Montenegro - Epert in reconstructions and visualizations.");
        Console.WriteLine("2. Dr. Jack Hodgins - Specialist in trace evidence analysis and entomology.");
        Console.WriteLine("3. Dr. Camille 'Cam' Saroyan - Forensic pathologist and head of the lab.");
        Console.WriteLine("4. Dr. Zack Addy - Brilliant but socially awkward forensic anthropologist.");
        Console.Write("Make a choice: ");

        var choice = Console.ReadLine();

        switch (choice)
        {
            case "1":
                partner = "Angela Montenegro";
                Angela = true;
                Console.WriteLine("\nYou choose Angela. Time to give the victim a face.");
                break;
            case "2":
                partner = "Dr. Jack Hodgins";
                Jack = true;
                Console.WriteLine("\nYou choose Hodgins. Maybe he can find microscopic clues.");
                break;
            case "3":
                partner = "Dr. Camille 'Cam' Saroyan";
                Cam = true;
                Console.WriteLine("\nYou choose Cam. She can figure out everything about the cause of death.");
                break;
            case "4":
                partner = "Dr. Zack Addy";
                Zack = true;
                Console.WriteLine("\nYou choose Zack. His analytical mind will definitely come in handy.");
                break;
            default:
                Console.WriteLine("\nInvalid choice, try again.");
                Console.WriteLine("Press any key to continue...");
                Console.ReadKey();
                Scene1();
                return;
                }
        Console.WriteLine("Press any key to continue...");        
        Console.ReadKey();        
        Scene1b();
    }
     
private void Scene1b() { // Plaats delict onderzoeken en aanwijzingen vinden    
Console.Clear();
    Console.WriteLine("You are in the car with Booth and " + partnerchoice1 + ". You step out of the SUV, the cold air biting at your skin.");
    Console.WriteLine("The Smithsonian National Museum of Natural History stands before you, its large glass facade illuminated by street lamps, while your footsteps echo on the marble stairs.");
    Console.WriteLine("Booth quickly walks to the entrance, but you, as always, can't help but let your thoughts drift to the puzzle before you.");
    Console.WriteLine("The museum is quiet, the atmosphere heavy with old history and science. The doors slide open, and you step inside, your eyes already searching for details—the crack in the floor, the smells of dust and old paper. The space is empty, the hall immense.");
    Console.WriteLine("Booth glances at you briefly, but it doesn't take long before you're focused on the case. \"The body must be here somewhere,\" he says, but you have already shifted your attention to the display cases along the walls.");
    Console.WriteLine("\"The temperature here is low, too low for a normal exhibit,\" you say, your voice almost always analytical. \"And the humidity... too high for preserving the mummies, this would speed up the decay process. What are they trying to hide?\"");
    Console.WriteLine("Booth looks up briefly but shrugs. \"You're right, but I'm more interested in the body.\"");
    Console.WriteLine("That's when you see the figure lying on the floor. In the middle of the hall lies the body of an unknown man, positioned in a strange, unnatural way. The surroundings also seem to point to something unusual.");
    Console.WriteLine("Booth immediately rushes to the body, but you quickly follow, your gaze already focused on the details. As you get closer, you begin to process the first clues.");
    Console.WriteLine("\"The clothing is modern, but seems torn. The position of the body suggests it wasn't accidentally placed—this looks deliberate,\" you say while looking at the body. Your eyes continue scanning the surroundings.");
    Console.WriteLine("\"The blood is fresh, but not enough to determine the time of death. We're dealing with a murder, not an accident.\"");
    Console.WriteLine("Booth, who is now inspecting the body, looks up at you. \"Yeah, I noticed that too. But we need to find out who this is.\"");
    Console.WriteLine("With a concentrated look, Booth begins to further examine the body, while you continue looking in silence, your thoughts already coming together into a logical conclusion.");
    Console.WriteLine("\"There is no reason why an archaeologist would be left here, among the mummies,\" you mutter, but Booth looks at you and says, \"We have a murder, Brennan. Let's figure out the identity.\"");
    Console.WriteLine("The phone rings, and after a short conversation, Booth hangs up. \"I have to go, Bones. But when you're done with your investigation, give me a call. We'll figure out what to do next.\"");

    Console.WriteLine("Press any key to continue...");
    Console.ReadKey();
    Scene1c();
}

private void Scene1c() {
        bool vitrinePlek = false;
    List<string> opties = new List<string>
    {
    "Look at the body and find characteristics to identify the victim.",
    "Use UV light to find traces of blood or other fluids.",
    "Call the lab to ask questions about something you found.",
    "Examine the other mummies, maybe just for fun. But also to see if there's anything suspicious. Especially because you're a bit distracted...",
    "Talk to the lab."
    };

                string labpartner = "";
                string labpartnerHijZij = "";
                if (partnerchoice1 == "Dr. Camille 'Cam' Saroyan"){
                 labpartner = "Dr. Zack Addy";
                 labpartnerHijZij = "He";
                }
                else if (partnerchoice1 == "Dr. Zack Addy"){
                 labpartner = "Dr. Camille 'Cam' Saroyan";
                 labpartnerHijZij = "She";
                }


    while (opties.Count > 0) // Blijft doorgaan totdat list leeg is
    {
        Console.Clear();
        Console.WriteLine("What do you want to do?");

        for (int i = 0; i < opties.Count; i++)
        {
            if (bloedigMes == false && opties[i] == "Call the lab to ask questions about something you found.")
            {
                Console.WriteLine($"{i + 1}. {opties[i]} [Locked]");
            }
            else
            {
                Console.WriteLine($"{i + 1}. {opties[i]}");
            }
        }

        Console.Write("Make a choice: ");
        if (int.TryParse(Console.ReadLine(), out int keuze) && keuze > 0 && keuze <= opties.Count)
        {  
            Console.Clear();
            string gekozenOptie = opties[keuze - 1];

            Console.WriteLine($"\nYou have chosen for: {gekozenOptie}");

            // Simuleer het vinden van een aanwijzing of niet
         if (bloedigMes == false && gekozenOptie == "Call the lab to ask questions about something you found.")
            {
                Console.WriteLine("This option is locked please chose another option.");
            Console.WriteLine("Press any key to continue...");        
            Console.ReadKey();
                continue;
            }
    else if (gekozenOptie == "Look at the body and find characteristics to identify the victim.") // Done 
            {
                gevondenClues.Add("Clue: The victim had a tattoo of a dragon on his arm.");
                Console.WriteLine("You have found an important clue: The victim had a tattoo of a dragon on his arm.");
                // Variabele om bij te houden of de clue gevonden is
                Console.WriteLine("\nBrennan kneels down next to the body and begins her examination.");

                Console.WriteLine("\n\"The victim is wearing a neat suit, but there are light dust particles on it. This indicates contact with a display case or an old object—possibly an artifact.\"");

                Console.WriteLine("\nShe carefully lifts the hand of the victim and examines the nails.");
                Console.WriteLine("\"There are traces of an old sand- or clay-like material under the nails. This is consistent with archaeological findings and suggests that he recently handled an artifact.\"");

                Console.WriteLine("\nBrennan then looks at the face of the victim and notes the following:");
                Console.WriteLine("\"The victim has a stab wound around his wraist and a bruise on his head. The bruise is not fatal, but the stab wound could be. Further examination is needed.\"");

                
                Console.WriteLine("\nBrennan looks at the arm of the victim and sees a tattoo of a dragon. Detailed, not recent. Possibly a symbol, a membership... Whatever it is this can help us identify him.\"");

                // Markeer de clue als gevonden
                clueDraakArm = true;

                Console.WriteLine("\n"+labpartner+" sighs. So we have poisoning, a fight or a fall, and now also a mysterious dragon tattoo. What do you want to do now, Bones?\"");
                opties.Remove(gekozenOptie);
                Console.WriteLine("Press any key to continue...");        
                Console.ReadKey();

            }
    else if (gekozenOptie == "Use UV light to find traces of blood or other fluids.")
            {
                gevondenClues.Add("Clue: There are traces of blood on the floor that lead to a display case.");
                Console.WriteLine("You have found an important clue: There are traces of blood on the floor that lead to a display case.");
                Console.WriteLine("\nYou take out your UV light and scan the area. The light reveals traces of blood on the floor, leading to a display case.");
                vitrinePlek = true;
                opties.Remove(gekozenOptie);
            Console.WriteLine("Press any key to continue...");        
            Console.ReadKey();
            }
    else if (gekozenOptie == "Examine the other mummies, maybe just for fun. But also to see if there's anything suspicious. Especially because you're a bit distracted...")
            {
                Console.WriteLine("You walk over to the mummies, your mind still on the victim and the clues you've found.");
                Console.WriteLine("You learn about the ancient civilizations, the rituals, and the customs that defined them. It’s fascinating, but you quickly realize that this is not the time to get distracted.");
                Console.WriteLine("You turn back to the victim and the case at hand.");
                opties.Remove(gekozenOptie);
            Console.WriteLine("Press any key to continue...");        
            Console.ReadKey();

            }
    else if (bloedigMes && gekozenOptie == "Call the lab to ask questions about something you found.")
            {                   
            Console.WriteLine("You call the lab and ask if they have received parts of the evidence");
            Console.WriteLine(labpartner + " says that they have received the bloodied knife and are examining it for fingerprints and other traces.");
            Console.WriteLine(labpartnerHijZij+" says that the knife has a strange symbol on the handle, similar to the tattoo on the victim's arm.");
            Console.WriteLine(labpartnerHijZij+" says that they will call you back as soon as they have more information.");
            opties.Remove(gekozenOptie);
            Console.WriteLine("Press any key to continue...");        
            Console.ReadKey();
            }
          

    else if(vitrinePlek && gekozenOptie == "Look under the display case.")
    {
        
        gevondenClues.Add("Clue: There is a bloody knife under a display case.");
        Console.WriteLine("You look around and see the display case where the blood traces lead. You walk towards it and notice something lying underneath.");
        Console.WriteLine("You crouch down and pick it up. It’s a bloody knife, sharp and dangerous. There are no fingerprints on it.");
        Console.WriteLine("However, there is a strange symbol on the handle.");
        Console.WriteLine("You keep the knife for further investigation.");
        bloedigMes = true;
        vitrinePlek = false;
        opties.Remove(gekozenOptie);
        Console.WriteLine("Press any key to continue...");        
        Console.ReadKey();

    }
        
    else if (gekozenOptie == "Talk to the lab."){
        Console.Clear();
        Console.WriteLine("You call the lab and ask if they have received any of the evidence yet and if they have found anything.");
        Console.WriteLine(labpartner + " shouts from a distance and says, 'I know who it is!'");
        Console.WriteLine("The victim had previously broken a pinky finger and a collarbone, and had recently suffered a leg fracture. There was only one person working at the museum who matched that description: Dr. Jeremy Donaldson.");
        Console.WriteLine("Press any key to continue...");
        Console.ReadKey();
        Console.Clear();
        Console.WriteLine("You call Booth and tell him who the victim was and that he worked at the museum.");
        Console.WriteLine("You tell Booth to bring all the staff to the station. Then we’ll question them together.");
        Console.WriteLine("You say that you and " + partnerchoice1 + " are coming to the FBI HQ and hang up.");
        Console.WriteLine("Press any key to continue...");
        Console.ReadKey();
        Scene2();
        
    }

        if (opties.Count == 1) // Alleen de optie "Praat met het Lab" is over //Dus automatisch Booth bellen
    {
        Console.Clear();
        Console.WriteLine("The lab calls you.");
        Console.WriteLine(labpartner + " shouts from a distance and says, 'I know who it is!'");
        Console.WriteLine("The victim had previously broken a pinky finger and a collarbone, and had recently suffered a leg fracture. There was only one person working at the museum who matched that description: Dr. Jeremy Donaldson.");
        Console.WriteLine("Press any key to continue...");
        Console.ReadKey();
        Console.Clear();
        Console.WriteLine("You call Booth and tell him who the victim was and that he worked at the museum.");
        Console.WriteLine("You tell Booth to bring all the staff to the station. Then we’ll question them together.");
        Console.WriteLine("You say that you and " + partnerchoice1 + " are coming to the FBI HQ and hang up.");
        Console.WriteLine("Press any key to continue...");
        Console.ReadKey();
        Scene2();
        return;
        }
          
        if (vitrinePlek && !opties.Contains("Look under the display case.")){
            opties.Add("Look under the display case.");
        }
        }

    else
    {
        Console.WriteLine("Invalid choice, please try again.");
        Console.WriteLine("Press any key to continue...");        
        Console.ReadKey();

        }



        

    // Als de speler ALLE onderzoeken heeft voltooid, wordt het lab automatisch gebeld.
    //laat dit niet zien als optie kiest met het lab spreken want dat gaat automatisch door naar de volgende scene
 
    }
            }
                 

private static void Scene2()
{
    Console.Clear();
    Console.WriteLine("You step into FBI HQ, the scent of coffee and paper filling the air. Booth is waiting for you at the entrance, his expression serious.");
    Console.WriteLine("He nods at you and leads you to one of the interrogation rooms, where the suspects are already waiting.");
    Console.WriteLine("\"Booth: Okay, Bones, let's make a bet. If this suspect says ‘I swear, I didn’t do anything’ within the first five minutes, you buy coffee. If he cries, I buy coffee.\"");  
    Console.WriteLine("\"Brennan: Statistically, suspects display defensive behavior within the first minute in 73% of cases, so your bet is rather biased.\"");  
    Console.WriteLine("\"Booth: Exactly. So... I’ll take a large with extra sugar.\"");
    Console.WriteLine("You arrive at the interrogation rooms, and Booth says: Okay, Bones, we have 9 suspects and witnesses to question. Who do you want to interrogate first?");

    List<string> personen = new List<string> 
    {
        "Dr. Edward 'Eddie' Langford (Suspect)",
        "Derek 'The Knife' Thompson (Suspect)",
        "Professor James 'Prof' Smith (Suspect)",
        "Jessica 'Jess' Taylor (Witness)",
        "Stop interrogating and call the lab to finally accuse the murderer."
    };

    Console.WriteLine("Press any key to continue...");
    Console.ReadKey();
    Console.Clear();
    
    while(personen.Count > 0)
    {
        Console.WriteLine("Choose a person to interrogate: ");
        for (int i = 0; i < personen.Count; i++)
        {
            Console.WriteLine($"{i + 1}. {personen[i]}");
        }
        Console.Write("Make a choice: ");
       
        if(int.TryParse(Console.ReadLine(), out int keuze) && keuze > 0 && keuze <= personen.Count)
        {
            Console.Clear();
            string gekozenPersoon = personen[keuze - 1];
            Console.WriteLine($"\nYou chose: {gekozenPersoon}");

            if(gekozenPersoon == "Dr. Edward 'Eddie' Langford (Suspect)")
            {
                Edward();
                personen.Remove(gekozenPersoon);
            }
            else if(gekozenPersoon == "Derek 'The Knife' Thompson (Suspect)")
            {
                Derek();
                personen.Remove(gekozenPersoon);
            }
            else if(gekozenPersoon == "Professor James 'Prof' Smith (Suspect)")
            {
                Prof();
                personen.Remove(gekozenPersoon);
            }
            else if(gekozenPersoon == "Jessica 'Jess' Taylor (Witness)")
            {
                Jessica();
                personen.Remove(gekozenPersoon);
            }
            else if(gekozenPersoon == "Stop interrogating and call the lab to finally accuse the murderer." || personen.Count == 1)
            {
                Scene3();
            }
            else
            {
                Console.WriteLine("Invalid choice, try again.");
                Console.ReadKey();
            }
        }
    }
}

private static void Edward() {
    Console.WriteLine("You interrogate Dr. Edward 'Eddie' Langford, an archaeologist who worked at the museum.");
    Console.WriteLine("He claims he wasn’t there that evening, but surveillance footage tells a different story.");
    
    Console.WriteLine("\nEdward: \"I wasn’t there! I swear!\"");
    
    Console.WriteLine("\nBooth: \"The surveillance footage says otherwise, Edward. What were you really doing there?\"");
    
    Console.WriteLine("\nEdward sighs and looks down.");
    Console.WriteLine("Edward: \"Okay, okay... I was there. I was studying the museum itself for a book I’m writing.\"");
    
    Console.WriteLine("\nBrennan: \"And why did you lie about it?\"");
    
    Console.WriteLine("\nEdward: \"Because the book is my life's work, and it contains many secrets that I only want to reveal to the world when I'm ready. No one, except for me and now you, knows that I’m writing a book. Please don’t tell anyone.\"");
    
    Console.WriteLine("\nYou’ve heard enough. Edward doesn’t seem to be the murderer.");
    Console.WriteLine("Press any key to continue...");
    Console.ReadKey();
    Console.Clear();
}

private static void Derek() {
    Console.WriteLine("You interrogate Derek 'The Knife' Thompson, a known art smuggler with a history of selling stolen museum pieces.");
    Console.WriteLine("His nickname comes from his love of knives... and there was a bloody knife near the body.");
    
    Console.WriteLine("\nDerek: \"I’ve got nothing to say.\"");
    
    Console.WriteLine("\nBooth: \"We know it was your knife, Derek. Why was it at the body?\"");
    
    Console.WriteLine("\nDerek: \"Yeah, it’s my knife. But I wasn’t there. I have an alibi.\"");
    
    Console.WriteLine("\nBrennan: \"And who could have stolen your knife?\"");
    
    Console.WriteLine("\nDerek: \"Only someone from the museum would have access to my knife.\"");
    
    Console.WriteLine("\nYou’ve heard enough. Derek could be the murderer. We now know that someone from the staff committed the murder.");
    Console.WriteLine("Press any key to continue...");
    Console.ReadKey();
    Console.Clear();
}

private static void Prof() {
    Console.WriteLine("You interrogate Professor James 'Prof' Smith, an expert in ancient cultures.");
    Console.WriteLine("He seems nervous and avoids eye contact.");
    
    Console.WriteLine("\nProf: \"I fell asleep in my office. I didn’t wake up until the alarm went off and the body was found.\"");
    
    Console.WriteLine("\nBooth: \"Why would someone enter your office and not wake you up?\"");
    
    Console.WriteLine("\nYou notice the professor has a slight tremor in his hands.");
    Console.WriteLine("Brennan: \"Professor, we found evidence that the victim was holding a valuable artifact. Can you explain why there was sand- or clay-like material under his nails?\"");
    
    Console.WriteLine("\nProf: \"I... I don’t know. Maybe he was working on an excavation.\"");
    Console.WriteLine("Booth: \"Or maybe he caught you stealing that artifact, and you tried to silence him.\"");
    
    Console.WriteLine("\nThe professor starts sweating and nervously looks around.");
    Console.WriteLine("Brennan: \"We also found a knife with a symbol matching the tattoo on the victim’s arm. Can you tell us about that?\"");
    
    Console.WriteLine("\nProf: \"That... that knife belongs to Derek. He has a thing for knives.\"");
    Console.WriteLine("Booth: \"But only someone from the museum would have access to that knife. And you had a motive to kill the victim.\"");
    
    Console.WriteLine("\nThe professor sighs deeply and closes his eyes.");
    Console.WriteLine("Prof: \"Lawyer. I want a Lawyer!\"");
    
    Console.WriteLine("\nYou’ve heard enough. The professor could be the murderer.");
    Console.WriteLine("Press any key to continue...");
    Console.ReadKey();
    Console.Clear();
}

    private static void Jessica() {
        Console.WriteLine("You interrogate Jessica 'Jess' Taylor, a young researcher who just started working at the museum.");
        Console.WriteLine("She found the body and is in shock.");
        
        Console.WriteLine("\nJessica: \"I... I found him there. I didn’t know what to do.\"");
        
        Console.WriteLine("\nBooth: \"Did you have a relationship with the victim?\"");
        
        Console.WriteLine("\nJessica nods slowly.");
        Console.WriteLine("Jessica: \"Yes, we were together. But I would never hurt him!\"");
        
        Console.WriteLine("\nBrennan: \"What were you doing that evening at the museum?\"");
        
        Console.WriteLine("\nJessica: \"I was working on a project. I heard a noise and went to check. That’s when I found him.\"");
        
        Console.WriteLine("\nYou’ve heard enough. Jessica doesn’t seem to be the murderer.");
        Console.WriteLine("Press any key to continue...");
        Console.ReadKey();
        Console.Clear();
    }

    private static void Scene3() {
    List<string> personen = new List<string>
    {
        "Dr. Edward 'Eddie' Langford",
        "Derek 'The Knife' Thompson",
        "Professor James 'Prof' Smith",
        "Jessica 'Jess' Taylor",
        "Ask Booth for help."
    };

    Console.Clear();
    Console.WriteLine("You call the lab and are informed that the knife had no fingerprints but did have a strange symbol on the handle. The same symbol you saw on the dragon tattoo.");
    Console.WriteLine("You look out the window at the suspects and witnesses you’ve just interrogated. Who is the murderer? And then it suddenly hits you...");
    Console.ReadKey();
    Console.Clear();

    while (personen.Count > 0) {
        Console.Clear();
        Console.WriteLine("Who did it?");
        for (int i = 0; i < personen.Count; i++) {
            Console.WriteLine($"{i + 1}. {personen[i]}");
        }

        if (int.TryParse(Console.ReadLine(), out int keuze) && keuze > 0 && keuze <= personen.Count) {
            Console.Clear();
            string gekozenPersoon = personen[keuze - 1];
            Console.WriteLine($"\nYou chose: {gekozenPersoon}");

            if (gekozenPersoon == "Dr. Edward 'Eddie' Langford") {
                Console.WriteLine("Booth says Edward is not the murderer. You look at the other suspects and witnesses.");
                personen.Remove(gekozenPersoon);
                Console.WriteLine("Press any key to continue...");
                Console.ReadKey();
            }
            else if (gekozenPersoon == "Derek 'The Knife' Thompson") {
                Console.WriteLine("Booth says Derek is not the murderer. You look at the other suspects and witnesses.");
                personen.Remove(gekozenPersoon);
                Console.WriteLine("Press any key to continue...");
                Console.ReadKey();
            }
            else if (gekozenPersoon == "Professor James 'Prof' Smith") {
                Console.WriteLine("Booth says the professor had debts and a motive to sell a valuable artifact.");
                Console.WriteLine("You look at him, and on his neck, you see part of the symbol you saw on the knife and the tattoo.");
                Console.WriteLine("It’s him, you shout.");
                Console.WriteLine("Booth nods and walks to the interrogation room to arrest the professor.");
                Console.WriteLine("Booth: \"Good work, Bones. We got the murderer.\"");
                Console.WriteLine("You’ve solved the case. Congratulations!");
                Console.WriteLine("Press any key to continue...");
                Console.ReadKey();
                Scene4(); // Scene 4: Congratulations and ending
                return;
            }
            else if (gekozenPersoon == "Jessica 'Jess' Taylor") {
                Console.WriteLine("Booth says Jessica is not the murderer. You look at the other suspects and witnesses.");
                personen.Remove(gekozenPersoon);
                Console.WriteLine("Press any key to continue...");
                Console.ReadKey();
            }
            else if (gekozenPersoon == "Ask Booth for help.") {
                Console.WriteLine("You decide to ask Booth for help.");
                Console.WriteLine("He points out that the professor had debts and a motive to sell a valuable artifact.");
                Console.WriteLine("You look at him, and on his neck, you see part of the symbol you saw on the knife and the tattoo.");
                Console.WriteLine("It’s him, you shout.");
                Console.WriteLine("Booth nods and walks to the interrogation room to arrest the professor.");

                Console.WriteLine("Press any key to continue...");
                Console.ReadKey();
                Scene4(); // Scene 4: Congratulations and ending
                return;
            }
            else {
                Console.WriteLine("Invalid choice, try again.");
                Console.ReadKey();
            }
        }
        else {
            Console.WriteLine("Invalid choice, try again.");
            Console.ReadKey();
        }
    }
}


private static void Scene4() 
{
    Console.Clear();
    Console.WriteLine("You’ve solved the case and arrested the murderer. Congratulations!");
    Console.WriteLine("You and Booth head to the bar 'The Founding Fathers' to celebrate.");
    Console.WriteLine("You order a glass of wine, and Booth orders a beer.");
    Console.WriteLine("Booth: \"Good work, Bones. You’ve done it again.\"");
    Console.WriteLine("Brennan: \"You were right about the bet. I'll buy you a coffee.\"");
    Console.WriteLine("Booth: \"How about a beer instead?\"");
    Console.WriteLine("You both laugh together.");
    Console.ReadKey();
    Console.WriteLine("Press any key to continue...");

    Console.Clear();
    Console.WriteLine("Congratulations, player! You've solved the murder!");
    Console.WriteLine("Thank you for playing my game!");

    Console.WriteLine("Created and developed by: Emre Kadir Tiren");
    Console.WriteLine("Press any key to exit the game...");
    Console.ReadKey();
    Environment.Exit(0);
}
    }
        }
