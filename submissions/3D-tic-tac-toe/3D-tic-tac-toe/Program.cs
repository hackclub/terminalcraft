using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection.Metadata.Ecma335;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Schema;

namespace _3D_tic_tac_toe
{
    internal class Program
    {
        static void Main(string[] args)
        {
            Console.ForegroundColor = ConsoleColor.Green;
            Console.Write(" ________  ________          _________  ___  ________          _________  ________  ________          _________  ________  _______\n|\\_____  \\|\\   ___ \\        |\\___   ___\\\\  \\|\\   ____\\        |\\___   ___\\\\   __  \\|\\   ____\\        |\\___   ___\\\\   __  \\|\\  ___ \\     \n\\|____|\\ /\\ \\  \\_|\\ \\       \\|___ \\  \\_\\ \\  \\ \\  \\___|        \\|___ \\  \\_\\ \\  \\|\\  \\ \\  \\___|        \\|___ \\  \\_\\ \\  \\|\\  \\ \\   __/|    \n      \\|\\  \\ \\  \\ \\\\ \\           \\ \\  \\ \\ \\  \\ \\  \\                \\ \\  \\ \\ \\   __  \\ \\  \\                \\ \\  \\ \\ \\  \\\\\\  \\ \\  \\_|/__  \n     __\\_\\  \\ \\  \\_\\\\ \\           \\ \\  \\ \\ \\  \\ \\  \\____            \\ \\  \\ \\ \\  \\ \\  \\ \\  \\____            \\ \\  \\ \\ \\  \\\\\\  \\ \\  \\_|\\ \\ \n    |\\_______\\ \\_______\\           \\ \\__\\ \\ \\__\\ \\_______\\           \\ \\__\\ \\ \\__\\ \\__\\ \\_______\\           \\ \\__\\ \\ \\_______\\ \\_______\\ \n    \\|_______|\\|_______|            \\|__|  \\|__|\\|_______|            \\|__|  \\|__|\\|__|\\|_______|            \\|__|  \\|_______|\\|_______|\n");
            Console.ForegroundColor = ConsoleColor.White;
            Console.WriteLine("Made with \u2764\ufe0f MrTinEU");
            Console.WriteLine("This is tic tac toe but with a twist, its played in 3-axis!");
            while (true)
            {
                
                Console.Write("Please enter the length of the field: ");
                int length = 0;
                int winlength = 0;
                try
                {
                    length = Convert.ToInt16(Console.ReadLine());
                }
                catch (Exception e)
                {
                    Console.WriteLine("Invalid input, please enter a number");
                    continue;
                }

                if (length < 2) 
                {
                    Console.WriteLine("Length can be smaller than 2");
                    continue;
                }
                Console.Write("Required length of sequence to win: ");
                try
                {
                    winlength = Convert.ToInt16(Console.ReadLine());
                }
                catch (Exception e)
                {
                    Console.WriteLine("Invalid input, please enter a number");
                    continue;
                }

                if (length < winlength)
                {
                    Console.WriteLine("Win length can't be bigger than field length");
                    continue;
                }
                if (winlength <= 1)
                {
                    Console.WriteLine("Win length can't be smaller than 2");
                    continue;
                }
                Console.Write("Enter player X nickname: ");
                string xname = Console.ReadLine();
                Console.Write("Enter player O nickname: ");
                string oname = Console.ReadLine();
                
                char[, ,] field = GenerateField(length);
                // 0-x 1-o
                int currentPlayer = 0;
                // game starts
                while (true)
                {
                    Console.Clear();
                    int currentZ = 0;
                    bool selectingCoordinates = false;
                    int x = 0, y = 0, z = 0;
                    while (true)
                    {
                        Console.Clear();
                        Console.WriteLine($"Current player: {(currentPlayer == 0 ? xname : oname)}");
                        Console.WriteLine($"Z axis: {currentZ}");
                        DisplayFieldPage(field, currentZ);
                        
                        Console.WriteLine("Use Up/Down arrows to change page (Z axis)");
                        Console.WriteLine("Press Enter twice to insert coordinates");
                        
                        ConsoleKeyInfo key = Console.ReadKey();

                        if (selectingCoordinates)
                        {
                            Console.Write("Enter coordinates in this order X Y Z with space in between: ");
                            string[] coordinates = new string[3];
                            try
                            {
                                coordinates = Console.ReadLine().Split(' ');
                            }
                            catch (Exception e)
                            {
                                Console.WriteLine("Invalid input");
                                continue;
                            }

                            try
                            {
                                x = Convert.ToInt32(coordinates[0]);
                                y = Convert.ToInt32(coordinates[1]);
                                z = Convert.ToInt32(coordinates[2]);
                            }
                            catch (Exception e)
                            {
                                Console.WriteLine("Invalid input");
                                continue;
                            }
                            if(x>=length || y>=length || z>=length || x<0 || y<0 || z<0)
                            {
                                Console.WriteLine("Invalid coordinates");
                                continue;
                            }
                            if (currentPlayer == 0)
                            {
                                field[x, y, z] = 'x';
                                break;
                            }
                            else
                            {
                                field[x, y, z] = 'o';
                                break;
                            }
                            
                        }
                        else
                        {
                            if (key.Key == ConsoleKey.UpArrow && currentZ < length - 1)
                            {
                                currentZ++;
                            }
                            else if (key.Key == ConsoleKey.DownArrow && currentZ > 0)
                            {
                                currentZ--;
                            }
                            else if (key.Key == ConsoleKey.Enter)
                            {
                                selectingCoordinates = !selectingCoordinates;
                            }
                            
                        }
                    }
                    int state = CheckState(field, winlength);
                    if (state == 0)
                    {
                        if (currentPlayer == 0)
                        {
                            currentPlayer = 1;
                        }else if (currentPlayer == 1)
                        {
                            currentPlayer = 0;
                        }
                        
                    }else if (state == 1)
                    {
                        Console.Write("Player ");
                        Console.ForegroundColor = ConsoleColor.Red;
                        Console.Write(xname);
                        Console.ResetColor();
                        Console.Write(" won!\n");
                        Console.Write("Do you want to play again? (y/n): ");
                        string answer = Console.ReadLine();
                        if (answer == "y")
                        {
                            break;
                            
                        }
                        else
                        {
                            return;
                        }
                       
                    }else if (state == 2)
                    {
                        Console.Write("Player ");
                        Console.ForegroundColor = ConsoleColor.Blue;
                        Console.Write(oname);
                        Console.ResetColor();
                        Console.Write(" won!\n");
                        Console.Write("Do you want to play again? (y/n): ");
                        string answer = Console.ReadLine();
                        if (answer == "y")
                        {
                            break;
                            
                        }
                        else
                        {
                            return;
                        }
                    }else if (state == 3)
                    {
                        Console.WriteLine("No more free space, it's a draw!");
                        Console.Write("Do you want to play again? (y/n): ");
                        string answer = Console.ReadLine();
                        if (answer == "y")
                        {
                            break;
                            
                        }
                        else
                        {
                            return;
                        }
                    }
                }
                
            }
            



        }


        static void DisplayFieldPage(char[,,] field, int page)
        {
            int length = field.GetLength(0);
            int maxDigits = GetDigitCount(length - 1); 

   
            Console.Write(new string(' ', maxDigits + 1)); 
            for (int i = 0; i < length; i++)
            {
                string columnHeader = i.ToString().PadRight(maxDigits) + " "; 
                Console.Write(columnHeader);
            }
            Console.Write("X");
            Console.WriteLine();

         
            for (int i = 0; i < length; i++)
            {
           
                Console.Write(i.ToString().PadRight(maxDigits + 1));
                for (int j = 0; j < length; j++)
                {
                    if (field[j, i, page] == 'x')
                    {
                        Console.ForegroundColor = ConsoleColor.Red;
                        Console.Write(field[j, i, page].ToString().PadRight(maxDigits) + " "); 
                        Console.ForegroundColor = ConsoleColor.White;
                    }
                    else if (field[j, i, page] == 'o')
                    {
                        Console.ForegroundColor = ConsoleColor.Blue;
                        Console.Write(field[j, i, page].ToString().PadRight(maxDigits) + " "); 
                        Console.ForegroundColor = ConsoleColor.White;
                    }
                    else
                    {
                        Console.Write(field[j, i, page].ToString().PadRight(maxDigits) + " "); 
                    }
                }
                Console.WriteLine();
            }
            Console.WriteLine("Y");
        }
        static int GetDigitCount(int number)
        {
            if (number == 0) return 1;
            return (int)Math.Floor(Math.Log10(Math.Abs(number))) + 1;
        }
        

        static char[,,] GenerateField(int length)
        {
            char[,,] field = new char[length, length, length];
            for (int i = 0; i < length; i++)
            {
                for (int j = 0; j < length; j++)
                {
                    for (int k = 0; k < length; k++)
                    {
                        field[i, j, k] = '_';
                    }
                }
            }
            return field;
        }

        
        static char[,,] GenerateRandomField(int length)
        {
            Random random = new Random();
            char[,,] field = new char[length, length, length];
            for (int i = 0; i < length; i++)
            {
                for (int j = 0; j < length; j++)
                {
                    for (int k = 0; k < length; k++)
                    {
                        
                        int randomNumber = random.Next(0, 3);
                        if (randomNumber == 0)
                        {
                            field[i, j, k] = 'x';
                        }else if (randomNumber == 1)
                        {
                            field[i, j, k] = 'o';
                        }
                        else
                        {
                            field[i, j, k] = '_';
                        }
                    }
                }
            }
            return field;
        }
        static int CountFreeSpaces(char[,,] field)
        {
            int length = field.GetLength(0);
            int count = 0;
    
            for (int x = 0; x < length; x++)
            {
                for (int y = 0; y < length; y++)
                {
                    for (int z = 0; z < length; z++)
                    {
                        if (field[x, y, z] == '_')
                        {
                            count++;
                        }
                    }
                }
            }
    
            return count;
        }
        //0 nikto nevyhral
        //1 x vyhral
        //2 o vyhral
        static int CheckState(char[,,] field, int win_length)
{
    int length = field.GetLength(0);
    if (win_length > length)
    {
        return -1;
    }

    // Check straight lines (X, Y, Z axes)
    for (int x = 0; x < length; x++)
    {
        for (int y = 0; y < length; y++)
        {
            // X axis check
            int countX = 0;
            int countO = 0;
            for (int i = 0; i < length; i++)
            {
                if (field[i, y, x] == '_')
                {
                    countX = 0;
                    countO = 0;
                }
                else if (field[i, y, x] == 'x')
                {
                    countX++;
                    countO = 0;
                    if (countX >= win_length)
                        return 1;
                }
                else if (field[i, y, x] == 'o')
                {
                    countO++;
                    countX = 0;
                    if (countO >= win_length)
                        return 2;
                }
            }

            // Y axis check
            countX = 0;
            countO = 0;
            for (int i = 0; i < length; i++)
            {
                if (field[x, i, y] == '_')
                {
                    countX = 0;
                    countO = 0;
                }
                else if (field[x, i, y] == 'x')
                {
                    countX++;
                    countO = 0;
                    if (countX >= win_length)
                        return 1;
                }
                else if (field[x, i, y] == 'o')
                {
                    countO++;
                    countX = 0;
                    if (countO >= win_length)
                        return 2;
                }
            }

            // Z axis check
            countX = 0;
            countO = 0;
            for (int i = 0; i < length; i++)
            {
                if (field[x, y, i] == '_')
                {
                    countX = 0;
                    countO = 0;
                }
                else if (field[x, y, i] == 'x')
                {
                    countX++;
                    countO = 0;
                    if (countX >= win_length)
                        return 1;
                }
                else if (field[x, y, i] == 'o')
                {
                    countO++;
                    countX = 0;
                    if (countO >= win_length)
                        return 2;
                }
            }
        }
    }

    // Check 2D diagonals in each plane
    for (int z = 0; z < length; z++)
    {
        // XY plane diagonals
        // Main diagonal (0,0) to (n-1,n-1)
        int countX = 0;
        int countO = 0;
        for (int i = 0; i < length; i++)
        {
            if (field[i, i, z] == '_')
            {
                countX = 0;
                countO = 0;
            }
            else if (field[i, i, z] == 'x')
            {
                countX++;
                countO = 0;
                if (countX >= win_length)
                    return 1;
            }
            else if (field[i, i, z] == 'o')
            {
                countO++;
                countX = 0;
                if (countO >= win_length)
                    return 2;
            }
        }

        // Anti-diagonal (0,n-1) to (n-1,0)
        countX = 0;
        countO = 0;
        for (int i = 0; i < length; i++)
        {
            if (field[i, length - 1 - i, z] == '_')
            {
                countX = 0;
                countO = 0;
            }
            else if (field[i, length - 1 - i, z] == 'x')
            {
                countX++;
                countO = 0;
                if (countX >= win_length)
                    return 1;
            }
            else if (field[i, length - 1 - i, z] == 'o')
            {
                countO++;
                countX = 0;
                if (countO >= win_length)
                    return 2;
            }
        }
    }

    for (int y = 0; y < length; y++)
    {
        // XZ plane diagonals
        // Main diagonal (0,0) to (n-1,n-1)
        int countX = 0;
        int countO = 0;
        for (int i = 0; i < length; i++)
        {
            if (field[i, y, i] == '_')
            {
                countX = 0;
                countO = 0;
            }
            else if (field[i, y, i] == 'x')
            {
                countX++;
                countO = 0;
                if (countX >= win_length)
                    return 1;
            }
            else if (field[i, y, i] == 'o')
            {
                countO++;
                countX = 0;
                if (countO >= win_length)
                    return 2;
            }
        }

        // Anti-diagonal (0,n-1) to (n-1,0)
        countX = 0;
        countO = 0;
        for (int i = 0; i < length; i++)
        {
            if (field[i, y, length - 1 - i] == '_')
            {
                countX = 0;
                countO = 0;
            }
            else if (field[i, y, length - 1 - i] == 'x')
            {
                countX++;
                countO = 0;
                if (countX >= win_length)
                    return 1;
            }
            else if (field[i, y, length - 1 - i] == 'o')
            {
                countO++;
                countX = 0;
                if (countO >= win_length)
                    return 2;
            }
        }
    }

    for (int x = 0; x < length; x++)
    {
        // YZ plane diagonals
        // Main diagonal (0,0) to (n-1,n-1)
        int countX = 0;
        int countO = 0;
        for (int i = 0; i < length; i++)
        {
            if (field[x, i, i] == '_')
            {
                countX = 0;
                countO = 0;
            }
            else if (field[x, i, i] == 'x')
            {
                countX++;
                countO = 0;
                if (countX >= win_length)
                    return 1;
            }
            else if (field[x, i, i] == 'o')
            {
                countO++;
                countX = 0;
                if (countO >= win_length)
                    return 2;
            }
        }

        // Anti-diagonal (0,n-1) to (n-1,0)
        countX = 0;
        countO = 0;
        for (int i = 0; i < length; i++)
        {
            if (field[x, i, length - 1 - i] == '_')
            {
                countX = 0;
                countO = 0;
            }
            else if (field[x, i, length - 1 - i] == 'x')
            {
                countX++;
                countO = 0;
                if (countX >= win_length)
                    return 1;
            }
            else if (field[x, i, length - 1 - i] == 'o')
            {
                countO++;
                countX = 0;
                if (countO >= win_length)
                    return 2;
            }
        }
    }

    // Check 3D diagonals
    // Diagonal from (0,0,0) to (n-1,n-1,n-1)
    int diagCountX = 0;
    int diagCountO = 0;
    for (int i = 0; i < length; i++)
    {
        if (field[i, i, i] == '_')
        {
            diagCountX = 0;
            diagCountO = 0;
        }
        else if (field[i, i, i] == 'x')
        {
            diagCountX++;
            diagCountO = 0;
            if (diagCountX >= win_length)
                return 1;
        }
        else if (field[i, i, i] == 'o')
        {
            diagCountO++;
            diagCountX = 0;
            if (diagCountO >= win_length)
                return 2;
        }
    }

    // Diagonal from (0,0,n-1) to (n-1,n-1,0)
    diagCountX = 0;
    diagCountO = 0;
    for (int i = 0; i < length; i++)
    {
        if (field[i, i, length - 1 - i] == '_')
        {
            diagCountX = 0;
            diagCountO = 0;
        }
        else if (field[i, i, length - 1 - i] == 'x')
        {
            diagCountX++;
            diagCountO = 0;
            if (diagCountX >= win_length)
                return 1;
        }
        else if (field[i, i, length - 1 - i] == 'o')
        {
            diagCountO++;
            diagCountX = 0;
            if (diagCountO >= win_length)
                return 2;
        }
    }

    // Diagonal from (0,n-1,0) to (n-1,0,n-1)
    diagCountX = 0;
    diagCountO = 0;
    for (int i = 0; i < length; i++)
    {
        if (field[i, length - 1 - i, i] == '_')
        {
            diagCountX = 0;
            diagCountO = 0;
        }
        else if (field[i, length - 1 - i, i] == 'x')
        {
            diagCountX++;
            diagCountO = 0;
            if (diagCountX >= win_length)
                return 1;
        }
        else if (field[i, length - 1 - i, i] == 'o')
        {
            diagCountO++;
            diagCountX = 0;
            if (diagCountO >= win_length)
                return 2;
        }
    }

    // Diagonal from (n-1,0,0) to (0,n-1,n-1)
    diagCountX = 0;
    diagCountO = 0;
    for (int i = 0; i < length; i++)
    {
        if (field[length - 1 - i, i, i] == '_')
        {
            diagCountX = 0;
            diagCountO = 0;
        }
        else if (field[length - 1 - i, i, i] == 'x')
        {
            diagCountX++;
            diagCountO = 0;
            if (diagCountX >= win_length)
                return 1;
        }
        else if (field[length - 1 - i, i, i] == 'o')
        {
            diagCountO++;
            diagCountX = 0;
            if (diagCountO >= win_length)
                return 2;
        }
    }

    // Check if it's a draw
    if (CountFreeSpaces(field) == 0)
    {
        return 3;
    }

    return 0;
}
    }
}
