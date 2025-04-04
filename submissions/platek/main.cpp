#include <iostream>
using namespace std;
#include <chrono>
#include <thread>
#include <random>


int main() {
    
    random_device rd;  // Urządzenie losujące (może być różne na różnych komputerach)
    mt19937 gen(rd()); // Generator Mersenne Twister
    uniform_int_distribution<int> dist(0, 11);
    
	int bizila;
	string text1, text2, text3;
	int i, j, k;
	string uwu[] = {"xoooo", "oxooo", "ooxoo", "oooxo", "oooox", "oooxo", "ooxoo", "oxooo"};
			
	string platki[] = {"*ooooooooooo", "o*oooooooooo", "oo*ooooooooo", "ooo*oooooooo", "oooo*ooooooo", 
	"ooooo*oooooo", "oooooo*ooooo", "ooooooo*oooo", "oooooooo*ooo",
	    "ooooooooo*oo", "oooooooooo*o", "ooooooooooo*" };
	
	string platek = "oooo*oooo";
	string pusta =  "ooooooooo";
	
	string tablica[] = {"oooooooooooo", "oooooooooooo", "oooooooooooo", "oooooooooooo", "oooooooooooo", 
	"oooooooooooo", "oooooooooooo", "oooooooooooo", "oooooooooooo"};
	




        
        for(j=0; j<=20; j++){
            std::cout << "\033[2J\033[H"; 
            for(i=0; i<=8; i++){
        	    cout<<tablica[i]<<endl;
        		//this_thread::sleep_for(chrono::seconds(1));
            }
            this_thread::sleep_for(chrono::milliseconds(700));
            for(i=8; i>=1; i--){
                tablica[i]=tablica[i-1];
            }
            int losowa = dist(gen); 
            string platek = platki[losowa];
            tablica[0]=platek;
            
        }
        //this_thread::sleep_for(chrono::milliseconds(500));


return 0;
}
