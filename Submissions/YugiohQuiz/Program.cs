using System.Net.Http;
using System.Reflection.Metadata;
using System.Threading.Tasks;

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
public string[] storeNames = {};
public int[] zipcodes = {99503, 99701, 99654, 35244, 36303, 36330, 35630, 35805, 35803, 35801, 35094, 35758, 36618, 36104, 35476, 36801, 36527, 72034, 72704, 72903, 72901, 72601, 71913, 72745, 72113, 72801, 72762, 85323, 86442, 85128, 86001, 85306, 85037, 85338, 85204, 85204, 85012, 85016, 86301, 85142, 85635, 85282, 85716, 85712, 85712, 85363, 85367, 85365, 91301, 94501, 91801, 92806, 92804, 95301, 91702, 93301, 93309, 93313, 93312, 90201, 90201, 94709, 94513, 93010, 91303, 91303, 95010, 95608, 91311, 95973, 91911, 95610, 92236, 93210, 94521, 94521, 90630, 95616, 95616, 91765, 91765, 90241, 94568, 94568, 92243, 92243, 94530, 91731, 95624, 95501, 94533, 92708, 94538, 93710, 93727, 93702, 95632, 92841, 95020, 91203, 95670, 93230, 90250, 90250, 92544, 92544, 92345, 91942, 91744, 91744, 92630, 90715, 93534, 93534, 90260, 91945, 94551, 95240, 90717, 93436, 90810, 90012, 90033, 90006, 90011, 90025, 90012, 95340, 92691, 92553, 92553, 92563, 94560, 91324, 94945, 92058, 91105, 95363, 91767, 91701, 91730, 92373, 93555, 92503, 95822, 95823, 95833, 95826, 92121, 94121, 94122, 94134, 91776, 95127, 95112, 92069, 94403, 92173, 93101, 95050, 95050, 93454, 93458, 95401, 91350, 91401, 93063, 90280, 90280, 95207, 95207, 94087, 95380, 91786, 95687, 91406, 93292, 93291, 80012, 80011, 80122, 80918, 80918, 80917, 80909, 80222, 80260, 80634, 80631, 80401, 80501, 80537, 81008, 06037, 06405, 06082, 06040, 06042, 06451, 06776, 06851, 06360, 06492, 20036, 19963, 19720, 19711, 19810, 33853, 34210, 32110, 33990, 32707, 34711, 32922, 33063, 32536, 33157, 33314, 32720, 32725, 32726, 33332, 33913, 32607, 32606, 33010, 33016, 33024, 32937, 32216, 32244, 32205, 33462, 33801, 33809, 33351, 32751, 33063, 32940, 33186, 34652, 34653, 33179, 32763, 32065, 32073, 32809, 32765, 32905, 32504, 33782, 33948, 34952, 34769, 34232, 34488, 32119, 32303, 33619, 33614, 33637, 32780, 33884, 31707, 31707, 31763, 30605, 39819, 30518, 30518, 30701, 30114, 30117, 31909, 30040, 30721, 30360, 30096, 30809, 30542, 30736, 30643, 31313, 30141, 30144, 30046, 30047, 31210, 30066, 30062, 30253, 30260, 30263, 30093, 31406, 30281, 30087, 31792, 31601, 30180, 30189, 96910, 96720, 96816, 96817, 50023, 50021, 50613, 52806, 50320, 52240, 50158, 50401, 50401, 51101, 83709, 83709, 83318, 83815, 83404, 83301, 83301, 60101, 60002, 60504, 60103, 61008, 60402, 60440, 60089, 62901, 60618, 60618, 60611, 60707, 60115, 62208, 60131, 61111, 61938, 61938, 62966, 60564, 60563, 60714, 60714, 62450, 61604, 61614, 61613, 61108, 60077, 62703, 62703, 60477, 61801, 60481, 60099, 46016, 46016, 47421, 47408, 46112, 47129, 47203, 46514, 47715, 47714, 46815, 46808, 46131, 46140, 46342, 46250, 46227, 46241, 46755, 46902, 47905, 47441, 46356, 46151, 46545, 47303, 47303, 46168, 46368, 47807, 67601, 66047, 66048, 66210, 66502, 66062, 67357, 67401, 66216, 67213, 67209, 67218, 41605, 42101, 40701, 42701, 41042, 40601, 40503, 40503, 40219, 40214, 40220, 40351, 40353, 42071, 42301, 41501, 42501, 70711, 70816, 71006, 71112, 70433, 70633, 70065, 70506, 70506, 70601, 71201, 01501, 01432, 02019, 02302, 02446, 01923, 02719, 01702, 02762, 02169, 01906, 01876, 02081, 01581, 01588, 01095, 21009, 21218, 21222, 20619, 20735, 20740, 21045, 21502, 20872, 21601, 21601, 21037, 21784, 21221, 20747, 21703, 21060, 21236, 21136, 20852, 21804, 04401, 04901, 04092, 48103, 49015, 48706, 48809, 48072, 48051, 48038, 48503, 48059, 48135, 49512, 49423, 48843, 49008, 49009, 48917, 48933, 49855, 48161, 48377, 48463, 48867, 48604, 48180, 49686, 48089, 48328, 48661, 49509, 48197, 55434, 55423, 56401, 55306, 55337, 55316, 55318, 55428, 55432, 55432, 55350, 56001, 55406, 55303, 55113, 56301, 55426, 55119, 55075, 55082, 63123, 65616, 63005, 65201, 63841, 63640, 64119, 64050, 63755, 64804, 65706, 65714, 63366, 65401, 64507, 65560, 65804, 65804, 63303, 64093, 65583, 39507, 39402, 39114, 38655, 39208, 39466, 39157, 39759, 38804, 39576, 59101, 59102, 59718, 59701, 59405, 28806, 28205, 28025, 28594, 28301, 28303, 28732, 28054, 27534, 28630, 28146, 27410, 27407, 27858, 27858, 28602, 27265, 27278, 28546, 28546, 27292, 28655, 27030, 28562, 27612, 27606, 27571, 28390, 28779, 27360, 27857, 28403, 28403, 27893, 27104, 58501, 58103, 58102, 58701, 68310, 68005, 68601, 68803, 68845, 68505, 68506, 68144, 68134, 69361, 03743, 03301, 03106, 03053, 03103, 03077, 03867, 07747, 07002, 08723, 07009, 08077, 07012, 08234, 07631, 08863, 07728, 08028, 08619, 07029, 07307, 07848, 08021, 07039, 08060, 07869, 07661, 07866, 08876, 07080, 08753, 07087, 08360, 08361, 87108, 87112, 87102, 87114, 88240, 88001, 87124, 87501, 87507, 89701, 89701, 89408, 89119, 89146, 89123, 89502, 89502, 89431, 89506, 12203, 12205, 14226, 13905, 10468, 11214, 11229, 11204, 14206, 12414, 14227, 14830, 11368, 13045, 10520, 11729, 11003, 12466, 11354, 11375, 14075, 14701, 11756, 14094, 11101, 11563, 13104, 10940, 13212, 10954, 10801, 12553, 10016, 12550, 14120, 13815, 11572, 13820, 12901, 13676, 12601, 12804, 11385, 14623, 11784, 10306, 13204, 13212, 11580, 13165, 13601, 14892, 11704, 10994, 45810, 44601, 44012, 45431, 44512, 44708, 45822, 45619, 45601, 45601, 45601, 43113, 43214, 43229, 45419, 44035, 45840, 45013, 45030, 45429, 44904, 44124, 44646, 44256, 44060, 43065, 44035, 44241, 45371, 43617, 43615, 44481, 43160, 44060, 43953, 43701, 74006, 74012, 74012, 74037, 73501, 73505, 73160, 73069, 74055, 74112, 74135, 97321, 97005, 97703, 97526, 97838, 97123, 97601, 97267, 97459, 97232, 97212, 97301, 97477, 97058, 97223, 16602, 16601, 18020, 19512, 17202, 18519, 15801, 19401, 16117, 16508, 16506, 16127, 19043, 15701, 15904, 18704, 17042, 19056, 17551, 15146, 15642, 19152, 19147, 19460, 15220, 15224, 15236, 19464, 19605, 19605, 18840, 17257, 18360, 18360, 15401, 18052, 17701, 17402, 17402, 00603, 00959, 00959, 00725, 983, 00969, 00682, 00676, 00717, 00926, 00693, 02860, 02893, 29406, 29210, 29212, 29223, 29527, 29501, 29445, 29615, 29072, 29673, 29730, 29678, 57006, 57701, 57106, 57110, 38320, 37416, 37042, 37316, 38501, 38108, 38018, 38555, 37643, 37072, 38305, 37604, 37601, 37923, 37919, 37921, 37355, 38112, 37813, 37217, 37821, 37830, 37388, 37388, 79605, 79109, 79106, 76013, 78748, 78705, 78705, 78602, 78521, 78526, 76028, 77840, 77301, 77384, 76522, 78413, 78413, 77429, 75224, 75208, 75204, 75020, 78537, 78541, 79902, 75234, 76133, 76116, 76140, 76108, 76244, 75402, 76548, 78550, 77070, 77077, 77055, 77077, 77036, 77041, 77043, 77338, 77340, 76053, 78634, 77565, 78028, 76542, 78363, 78640, 78040, 78040, 75067, 75068, 75604, 79401, 79416, 75901, 78501, 75149, 79701, 76065, 75773, 77459, 76180, 75081, 77469, 76903, 76901, 78216, 78227, 78238, 78666, 78155, 75090, 76504, 75160, 75504, 75701, 75707, 78148, 77662, 76711, 78596, 84010, 84015, 84041, 84405, 84404, 84403, 84062, 84405, 84067, 84104, 84070, 84094, 84660, 84660, 84015, 84129, 84088, 22202, 24060, 20121, 22901, 22701, 24541, 22030, 22033, 22401, 23666, 23860, 24501, 24112, 23608, 23503, 23701, 23228, 23225, 24016, 22150, 23452, 23188, 24293, 24382, 00802, 05201, 05403, 98520, 98225, 98312, 98337, 98532, 99403, 98823, 98201, 98338, 98503, 98632, 98273, 98371, 98057, 98133, 98104, 98383, 98290, 99223, 99205, 99206, 98444, 98406, 99362, 98902, 98901, 54914, 54915, 53913, 53007, 53115};
public string[] locations = {"2301 Spenard Road", "418 3rd St.", "500 Swanson Ave.", "2015 Valleydale RD", "3201 Montgomery Hwy", "621 Boll Weevil Circle", "248 Seville Street", "2620 Clinton Ave West", "12021 Memorial Pkwy S", "2205 Mock Road SW", "8033 Parkway Dr.", "7425 Hwy 72 West", "5701 Moffett Rd", "910 Adams Avenue", "935 McFarland Blvd.", "3909 Pepperell Pkwy", "6450 US-90", "690 Shelby Trail", "6302 Wilkerson", "5111 Rogers Ave", "923 Louisville St", "125 Industrial Park Road", "3812 Central Ave", "106 N Bloomington St", "9871 Maumelle Blvd", "407 N Arkansas Ave", "5320 W Sunset Ave", "965 E Van Buren St", "2580 Highway 95", "1024 N Arizona Blvd", "1471 S Milton", "4340 W Thunderbird Rd.", "6808 N. Dysart Rd.", "756 N. Dysart Rd.", "2639 E Broadway Rd", "1107 S Gilbert Rd", "4747 N Central Ave", "1602 E Indian School Rd", "1841 E AZ-69 #100", "18510 E San Tan Blvd 111", "2200 El Mercado Loop", "3415 S. McClintock Dr.", "238 S Tucson Blvd", "4444 East Grant Road", "5801 E Speedway Blvd", "11122 W. Alabama Ave.", "11411 South Fortuna Rd", "1401 South yuma palms Parkway", "5214 Chesebro Rd.", "650 Central Ave.", "39 S Garfield Ave", "1538 N State College Blvd", "2424 W. Ball Road", "2820 Shaffer Rd", "857 S Lark Ellen Ave", "1101 18th Street", "5456 California Ave", "6225 District Blvd.", "9660 Hageman Rd", "4219 Gage Ave", "7508 Eastern Ave", "1797 Shattuck Ave", "2430 Sand Creek Road", "2270 Ventura Blvd.", "6600 CA-27", "21425 Sherman Way", "1855 41st Ave", "6026 Fair Oaks Blvd.", "9449 De Soto Ave", "2540 Esplanade", "1417 Hilltop Drive", "6916 Sunrise Blvd", "1695 7th St", "192 E Elm Ave", "4425 J Treat Boulevard", "4375 Clayton Rd", "9975 Walker St", "1790 East 8th St", "654 G Street", "21308 Pathfinder Rd", "950 N Diamond Bar Blvd", "8711 Firestone Blvd", "6715 DUBLIN BLVD", "6700 Amador Plaza Road", "2299 W Adams Ave", "549 W Main Street", "4060 El Cerrito Plz", "10959 Main St", "9139-2 E. Stockton Blvd.", "3300 Broadway", "1325 Gateway Blvd.", "11213 Slater Ave", "40 Fremont Hub Courtyard", "464 E Bullard Ave Ste 103", "5150 E. Kings Canyon Rd", "3215 E. Tulare", "10550 Twin Cities Road", "7411 Garden Grove Blvd", "8300 Arroyo Circle", "123 W. Wilson Ave", "2230 Sunrise Blvd", "214 N. Irwin St.", "13535 Inglewood Ave", "4204 East Florida Avenue", "2140 E. Florida Ave", "16727 Bear Valley Rd.", "9019 Park Plaza Dr", "16350-C Valley Blvd", "15819 Main St.", "23615 El Toro Road", "12606 Del Amo Blvd", "42035 12th St W", "512 W Lancaster Blvd", "4451 Redondo Beach Blvd", "7943 Broadway", "1342 N Vasco Rd", "920 South Cherokee Lane", "24017 Narbonne Ave", "105 West Ocean Avenue", "1882 Santa Fe Ave", "319 E 2nd St", "2036 Cesar E Chavez Ave", "1243 S Alvarado St", "1356 E 41st St", "11304 Santa Monica Blvd", "232 E 2nd St.", "1636 Canal St.", "23854 Via Fabricante", "12625 Frederick St.", "22500 Town Circle Street", "39815 Alta Murrieta Road C-6", "5970 Mowry Ave", "8820 Reseda Blvd", "1205 Grant Ave", "3365 Mission Ave", "770 S. Arroyo Pkwy", "515 Keyston Blvd.", "883 E Holt Ave", "6658 Carnelian St", "9155 Archibald Ave", "19 E Citrus Ave", "901 S. China Lake Blvd", "10128 Indiana Ave", "6220 Belleau Wood Lane", "8241 Bruceville Rd", "3291 Truxel Rd.", "9121 Kiefer Blvd", "5995 Mira Mesa Blvd.", "5424 Geary Blvd", "1342 Irving Street", "25 Burrows St", "261 S San Gabriel Blvd", "2842 Story Road", "969 Story Rd", "635 N Twin Oaks Valley Rd #4", "4212 Olympic Ave", "4630 Border Village Rd", "6 W Anapamu", "1171 Homestead Rd.", "2855 Stevens Creek Blvd", "159 Town Center East", "208-B W Main St", "1901 Cleveland Ave A", "26771 Boquet Canyon", "14109 Burbank Blvd", "1960 Sequoia Avenue", "9300 California Ave", "4367 Tweedy Blvd.", "2233 Grand Canal Blvd", "1224 Monaco Ct", "781 E El Camino Real", "139 N. Center St", "325 N 2nd Ave", "1919 Peabody Road", "17218 Saticoy Street", "1643 E Main St", "107 E. Main St.", "1250 S. Abilene St", "15343 E 6th Ave", "2510 E Arapahoe Rd", "4341 N. Academy Blvd.", "4420 Austin Bluffs Pkwy", "4765 North Carefree Circle", "2427 North Academy Blvd", "2120 S Holly St", "8410 Umatilla St", "2700 W. 10th St", "1705 9th St.", "14500 W Colfax Ave", "1515 Main Street", "1730 W Eisenhower Blvd", "4065 Club Manor Drive", "848 Farmington Avenue", "221 West Main St", "483 Enfield St", "52 Purnell Place", "194 Buckland Hills Dr.", "470 Lewis Ave", "221 Danbury Rd", "295 Westport Avenue", "276 West Main Street", "220 North Colony St.", "2010 P Street NW", "3 North Walnut St", "807 Churchmans Rd", "173 E. Main St.", "3615 A Silverside Rd", "1429 Resmondo Drive", "8208 Cortez Rd", "3389 North State St", "311 Del Prado Blvd S", "3385 S US HIGHWAY 17/92", "194 US HIGHWAY 27", "801 Dixon Blvd", "1447 Lyons Road", "743 Ashley Dr", "10675 SW 190th Street", "4343 S St RD 7", "502 N Spring Garden Ave", "1878 Providence Blvd.", "113 N Bay Street", "6941 SW 196th Ave", "10676 Colonial Blvd", "3601 SW 2nd Ave", "2441 NW 43rd St.", "56 E 5th Street", "7342 W 20TH AVE", "6867 Taft St.", "991 E Eau Gallie Blvd", "8595 Beach Blvd", "8102 Blanding Blvd", "2740 Park Street", "6222 S Congress ave #E2", "4836 U.S. 92", "5173 US 98 North", "4580 N. University Dr.", "8550 S. HWY 17-92", "1440 SR-7 N", "5325 N. Wickham Road", "12550 SW 88th Street", "6347 Masachusets Ave", "8507 Old County Rd 54", "20725 NE 16th Ave", "2411 E Graves Ave", "1101 Blanding Blvd", "1932 Park Avenue", "7671 Orange Blossom Trail", "3228 W State Rd 426", "4651 Babcock ST NE", "6895A North 9th Ave", "9600 66th St. N", "1441 Tamiami Trail", "8906 S US Highway 1", "1220 11 Street", "935 N Beneva Road", "14209 East Highway 40", "565 Beville Rd", "3840 North Monroe St", "10101 E Adamo Dr", "4350 West Waters Ave #206", "13316 Telecom Dr", "3550 S Washington Ave", "6260 Cypress Gardens Blvd", "2601 Dawson Road", "2610 Dawson Road", "1104 Westover Blvd", "1961 Barnett Shoals Rd.", "1121 E. Shotwell St.", "4264 Sudderth Rd.", "1350 Buford Highway", "265 Hwy 53", "116 Riverstone Pkwy", "225 Lovvorn Rd", "7830 Veterans Parkway", "540 Lake Center Pkwy", "2708 Airport Rd", "6035 Peachtree RD", "3650 Satellit Blvd.", "672 Mullins Colony Drive", "7400 Spout Springs Rd", "4079 Cloud Springs Road", "150 West Franklin St.", "108 South Commerce Street", "4215 Jimmy Lee Smith Pkwy", "3895 Cherokee St NW #610", "116 East Crogan St", "4800 Lawrenceville Hwy", "3076 Riverside Dr", "3372 Canton Road", "1803 Roswell Rd", "569 Jonesboro Road", "2270 Lake Harbin Rd", "66 Bullsboro Dr", "4935 Jimmy Carter Blvd", "7400 Abercorn St", "1005 Brentwood Pkwy", "5385 Five Forks Trickum Rd SW", "1210 E Jackson St", "507 N Patterson St", "451 West Bankhead Hwy", "6721 Bells Ferry Rd", "230 West Soledad Avenue", "57 Shipman St", "3160 Waialae Ave", "650 Iwilei Rd", "510 SW 3rd Street", "1605 SE Delaware Ave.", "602 State Street", "102 E Kimberly Rd", "3315 SE 14th St", "115 South Linn Street", "2501 South Center St", "2468 4th St SW", "221 N. Federal", "823 Gordon Drive", "7211 W Colonial St.", "7079 Overland Rd.", "1650 Overland Ave.", "245 W Sunset Ave", "2099 E 17th St", "1037 Blue Lakes Blvd North", "756 Falls Ave", "1135 W National Ave", "911 Main Street", "195 Fox Valley Center Drive", "116 W. Bartlett Ave.", "505 S State", "7122 Ogden Ave", "623 East Boughton Road", "404 W Half Day Rd.", "207 W. Main St.", "2028 W. Montrose", "3804 N Western Ave", "835 N Michigan Ave", "7000 W Diversey", "811 West Lincoln Highway, Store #1", "1977 W US HWY 50", "9704 W Franklin Ave", "5600 N 2nd St", "201 Richmond Ave East", "1622 Broadway Ave.", "1003 Chestnut St", "4003 Plainfield-Naperville Road", "710 E Ogden Ave", "233 Golf Mill CTR", "7637 N Milwaukee Ave.", "104 E. Main St.", "3010 N Sterling Ave", "3915 N Sheridan Rd", "2200 War Memorial Dr", "3925 E. State Street", "4999 Old Orchard Center Space E-11", "1820 Adlai Stevenson Dr", "2761 S 6th St.", "8010 W 171st Street", "123 W Main St", "223 N Water St", "1711 Lewis Ave.", "111 E 10th Street", "1610 S Scatterfield Road", "2821 WASHINGTON AVE.", "223 S. Pete Ellis Dr.", "1060 E Main St", "709B E. Lewis and Clark Parkway", "3920 25th St", "1900 Berry Street", "999 N Congress Ave", "2717 Covert Ave.", "2126 Inwood Drive", "1509 Goshen Ave", "1884 Northwood Plaza", "1040 N. State St", "154 S Illinois St", "6020 E 82nd St", "7307 US 31", "5707 W. Morris", "115 S Main St", "300 East Southway Boulevard", "2133 S. 4th St.", "1160 A St Se", "410 E. Commercial Ave.", "77 E Washington St", "620 W Edison Rd.", "1712 W University Ave", "418 E Mcgalliard Road", "1702 E. Main St.", "3369 Willowcreek Rd", "248 South 7th St", "200 E 8th Street", "2329 Iowa St.", "720 Shawnee", "13354 College Blvd", "515 Fort Riley Blvd.", "113 S Mur-Len Rd", "110 South 18th Street", "2259 South 9th Street Lot 14", "12616 W. 62nd Terrace", "2431 W Pawnee St", "4800 W. Maple", "4900 E Pawnee St.", "11085 US Highway 23 S", "1337 US 31 W BY PASS", "1406 W. Cumberland Gap PKWY.", "5571 North Dixie Hwy", "8870 Bankers St", "1100 US Highway 127 S", "3401 Nicholasville Road", "4801 Outer Loop", "5534 New Cut Rd", "1850 S Hurstbourne Pkwy", "149 East Main Street", "874 Indian Mound Drive", "808 Chestnut St STE C", "4786 Frederica St.", "4163 North Mayo Trail", "2085 Lantern Ridge Dr", "52 Eury Ln", "28550 Hwy 43", "10330 Airline Highway", "5608 Benton Rd", "4100 Barksdale Blvd", "2033 N Hwy 190", "801 E. Fourth Street", "3712 Williams Blvd.", "120 Curran Ln", "1512 Ambassador Caffery Parkway", "614 West Prien Lake Road", "2221 Louisville Ave.", "385 Southbridge St", "41 Main Street", "15 N MAIN ST", "675 Centre St.", "75 High St", "67 Huttleston Ave", "60 Worcester Road", "2 Wilkins Drive", "1357 Hancock Street", "910 Broadway", "1830 Main St", "1335 Main St", "153 Turnpike Rd", "1167 Providence Rd", "2460 Boston Rd", "2909 Emmorton Rd", "2125 Maryland Avenue", "7620 German Hill Road", "22599 MacArthur Blvd", "6449 Old Alexandria Ferry Road", "4748 Cherry Hill Road", "9400 Snowden River Pkwy", "1262 Vocke Rd", "26212 Ridge Road", "415A E Dover St", "8223 Elliott Rd", "133 Mitchells Chance Rd.", "1209 Liberty Road", "1546 Eastern Blvd", "7898 Cryden Way", "5500 Buckeystown Pike", "7602 Baltimore Annapolis BLVD", "7902 Belair", "17 Main Street", "11772 Parklawn Dr", "8249B Dickerson Ln", "268 Odlin Rd", "67 E Concourse", "492 Main St", "2121 W Stadium Blvd", "669 Capital Ave SW", "3980 E. Wilder Rd", "215 E State St", "2666 Coolidge Hwy", "50720 Gratiot Avenue", "20564 Hall Road", "706 W Court Street", "4350 24th Ave", "32647 Ford Rd", "3661 28th Street SE", "1036 Washington Ave", "4308 S. Westnedge Ave.", "5029 West Main Street", "932 Elmwood Rd", "216 Washington Square", "329 West Washington Street", "1211 S Monroe St", "45049 W Pontiac Trail", "275 South State Rd", "1395 E. Main St.", "3029 Bay Plaza Dr", "22725 Wick Rd", "1043 W South Airport Rd", "1400 Scott Lake Rd", "132 W. Houghton Ave", "5316 Clyde Park AVE SW", "724 County Highway 10 NE", "9052 Lyndale Ave. S", "14136 Baxter Drive", "14332 Burnhaven Dr", "12450 River Ridge Lane", "11591 Theatre Drive N.", "230 Pioneer Trail", "5560 W Broadway Ave", "1091 E. Moore Lake Dr", "1206 E Moore Lake Drive", "1060 Highway 15 S", "903 S Front St", "4701 Hiawatha Ave", "14041 St Francis Blvd NW", "1143 Larpenteur Avenue West", "88 33rd Ave S", "3015 Utah Ave South", "1994B Suburban Ave", "207 13th Ave South", "1305 Frontage Rd W", "84 Grasso Plaza", "670 Branson Landing Blvd", "18533 Outlets Blvd.", "111 S Ninth Street", "221 North Walnut", "447 E. Karsh Blvd.", "6041 NE Antioch Rd", "107 W Lexington", "528 W Main St", "801 E 20th St 7-A", "1190 Spur Drive", "106 W Sherman Way", "258 Fort Zumwalt Square", "814 N Pine St", "1401 S Belt Highway", "404 W 4th Street", "2825 S Glenstone Ave", "3309-A E. Sunshine", "1106 Jungs Station Rd", "207 North Holden", "320 Ichord Avenue", "55 Hardy Court Shopping Center", "4700 Hardy St", "105 Main Street N", "303 Heritage Drive", "438 N Bierdeman Road", "211 Williams Ave", "731 S Pear Orchard Rd", "418 E LEE BLVD", "3196 Tupelo Commons", "407 US 90", "1140 First Ave N", "2059 Broadwater Ave", "2740 West Main St.", "127 N Main ST", "909 13th Street South", "505 New Leicester Highway", "1224 Commercial Ave", "4 Union St N", "8700 Emerald Dr.", "1330 Bragg Boulevard", "560 N Reilly Rd", "3049 Hendersonville Rd", "401 Cox Rd", "204 South Berkeley Blvd", "130 Pinewood Rd", "409 South Salisbury Ave", "1820 Pembroke Rd", "5002 High Point Rd", "2713 East 10th St", "1400 Charles Blvd.", "555 US HWY 70 SW", "3805 Tinsley Dr.", "110 Boone Square St.", "155 Brynn Marr Rd.", "102 Western Blvd", "110 Cotton Grove Rd", "902 West Union St", "249 Market Street", "112 South Business Plaza", "5910 Duraleigh Road", "5563 Western Boulevard", "416 S. Main Street", "1044 Lillington Hwy", "130 Sylva Plaza", "36 West Main Street", "1839 South Main Street", "5015 Wrightsville Ave", "4107 Oleander Dr", "2801-1B Ward Blvd", "4007 C Country Club Rd", "801 E Main Ave", "3902 13th Ave S", "2501 7th Ave N", "121 Main Street South", "320 E Court Street", "1406 Harlan Dr.", "2462 32nd Ave", "2108 Lawrence Lane", "5012 3rd Avenue", "1415 N. Cotner Blvd", "4107 Pioneer Woods Dr.", "14616 West Center Road", "2311 N 90th St", "2302 Frontage Rd.", "42 opera house square", "341 Louden Rd", "1134 Hooksett Rd", "123 Nashua Road", "252 Willow St", "66 Route 27", "37 N Main Street", "1077C Route 34", "185 Broadway", "2950 Yorktowne Blvd", "555a Pompton Ave", "1204 Rt 130", "120 Market St", "3003 English Creek Ave", "35 South Van Brunt St", "45 Lafayette Rd", "3710 US HWY 9", "30 N. Main Street", "2103 Whitehorse Mercerville Rd", "725 Harrison Ave", "298 Central Ave", "75 Rt. 15", "100 N. White Horse Pike", "93 East Mt. Pleasant Ave", "1690 RT 38", "540 Rt 10", "26 River Edge Road", "301 Mt Hope Ave", "5 Division St", "2325 PLAINFIELD AVE", "43 Main Street", "2103 Summit Ave", "301 S Main Rd", "1370 S. Main Rd.", "530 Washington St NE", "11130 Lomas Blvd NE", "600 Central Ave SE", "9311 Coors Blvd NW", "2827 N Dal Paso", "1615 N Solano", "1700 Southern Blvd SE", "516 N Guadalupe", "4250 Cerrillos Road", "1966 E. William St.", "3189 US Highway 50 E", "805 E Main St", "6521 Las Vegas Blvd South", "5620 W CHARLESTON BLVD #110", "500 E Windmill Ln", "5460 Meadowood Mall Circle", "3961 S McCarren Blvd", "1188 Victorian Plaza Circle", "2308 Oddie Blvd", "1 Crossgates Mall Road", "1238 Central Ave", "3098 Maple Road", "1235 Upper Front St", "2391 Grand Concourse Store 1", "8648 18th Ave", "1685 E. 15th St.", "6120 18th Avenue", "85 South Rossler Ave", "369 Main St", "43 Kelly Dr", "11 E Pulteney St", "112-02 Roosevelt Ave", "75 E Court St", "35 North Riverside Ave.", "1883B Deer Park Ave.", "1303 Hempstead Turnpike", "175 Broadway FL 1", "133-18 39th Ave, Lower Level", "96-11 Metropolitan Ave", "4751 Southwestern Boulevard", "707 Fairmount Ave", "2711 Hempstead Turnpike", "136 Walnut Street", "34-09 Queens Blvd", "486 Merrick Road", "315 Fayette St.", "65 Dolson Ave", "628 S. Main St.", "347 West Route 59", "237 A Main St", "1012 Little Britain Rd.", "431 5th Ave. 2nd Floor", "280 LITTLE BRITAIN RD", "1089 Kinkead Ave", "10 South Broad St.", "2833 Long Beach Road", "154 Main Street", "60 Smithfield Blvd.", "24 Market St", "2001 South Road, #C204", "74 Quaker Rd.", "60-73 Mytrle Ave", "1225 Jefferson Road", "1244 Middle Country Rd", "299B New Dorp Lane", "689 North Clinton St.", "6035 East Taft Road", "175 Rockaway Ave", "655 NY-318", "253 State St", "441 Chemung St", "70 Route 109", "3720 Palisades Center Dr", "113 N Main St", "1100 E State St.", "33382 Walker Road", "2727 Fairfield Commons Blvd", "52 Boardman-Canfield Rd", "1314 Whipple Ave. NW", "202 S Sugar Street", "8 Chesapeake Plaza", "615 Central Center", "617 1/2 Central Center", "2055 N Bridge St", "24753 US Highway 23 S", "4256 N. High St.", "1489 Schrock Road", "458 Patterson Rd", "558 Cleveland St", "441 East Sandusky St", "1224 Main St.", "1151 Stone Dr E5", "1217 Stroop Road", "305 E Main St", "5646 Mayfield Road", "4304 Lincoln Way E", "110 W. Washington St.", "7249 Center Street", "8731 Smoky Row RD", "5204 Detroit Rd", "9258 Market Square Drive", "30 E. Main St", "6725 W Central Ave", "5960 Angola Rd", "161 W. Market St.", "107 South Main Street", "34955 Chardon Road", "538 Main St.", "3575 Maple Ave", "574 SE Washington Blvd", "745 N Aspen Ave", "1825 S Aspen Avenue", "508 E A Street", "916 SW F Ave", "1040 Northwest 38th Street", "625 N. Moore Ave", "121 24th Ave NW", "12656 E 86th Pl N", "4622 East 11th Street", "3944 S. Hudson Ave.", "425 Jackson St SE", "13227 SW Canyon Rd", "3188 N Hwy 97", "100 NE Midland Ave", "1055 S Hwy 395", "238 SE Washington St", "915 Pine St", "17185 SE McLoughlin Blvd", "761 Virginia Ave", "1220 Lloyd Center 2nd Floor", "736 NE Martin Luther King Jr Blvd", "241 Commercial St. NE", "1843 Pioneer Parkway East", "314 East 2nd Street", "11940 Sw Pacific Hwy", "3200 Pleasant Valley BLVD", "1130 12th avenue", "224 Nazareth Pike", "125 E. Philadelphia Ave", "868 Lincoln Way West", "849-851 Main St", "351 West Long Ave", "213 W Germantown Pike", "516 Lawrence Ave", "642 West 26th St", "2411 West 26th Street", "25 Pine Grove Square", "2129 MacDade Blvd", "1450 Oakland Ave.", "500 Galleria Drive", "738 Wyoming Ave", "625 Cumberland Street", "4354 New Falls Road", "250 Manor Ave", "4053 William Penn Hwy", "12120 Lincoln Highway", "7907 Bustleton Ave", "521-525 South 5th Street", "275 Schuylkill Rd", "1002 Greentree Road", "4707 Liberty Ave", "310 Curry Hollow Rd", "214 E High St", "2910 N 5th Hwy Street", "3405 N 5th St Highway", "515 S Keystone Ave", "45 West King Street", "344 Stroud Mall Rd", "580 Main Street", "1318 Mall Run Rd", "257 Lehigh Valley Mall", "637 Rose Street", "2512 Eastern Blvd", "4464 Lincoln Highway East", "Carr 107 KM 2.8 West Professional Building", "1236 Avenida Main", "31-47 Avenida Main, Urb Santa Rosa", "13 Calle Munoz Rivera", "URB VALLE ARRIBA HEIGHTS AB13 CALLE M", "9 Calle Jose Julian Acosta", "2770 Ave. Hostos", "Calle Don Chemary", "URB. Villa Grillasca Ave, Munoz Rivera", "359 Calle San Claudio", "Urb. Brasilia C-29 Calle 2 Segundo Piso I", "545 Pawtucket Ave", "297 Providence Street", "2150 Northwoods Blvd", "736c St Andrews Rd", "275 Harbison Blvd", "7201 Two Notch Road", "110A El Bethel Rd", "1641 W. Palmetto St.", "1230 Red Bank Rd", "2301 Wade Hampton Blvd", "5060 Sunset Blvd", "2615 Hwy 153", "2301 Dave Lyle Blvd", "115 E North 1st St", "420 4th St", "4331 Triple Crown Dr.", "7218 W 41st St", "1914 S Sycamore Ave", "201 Fern Ave", "5864 Brainard Rd", "287 Stonecrossing Dr", "200 Paul Huff Pkwy", "880 W. Jackson St", "8551 Macon Rd.", "823 Exocet Drive", "21 Fountain Sq", "819 Broad Street", "1000 Rivergate Parkway", "278 Parkstone Place", "3302 W Market St", "430A Salem Avenue", "390 NW Loop", "4747 Hwy 6", "9155 Blvd 26", "905 N. Jupiter Rd.", "1301 FM 2218, Suite 500B", "113 E Concho Ave", "3230 Sherwood Way", "13013 N. US-Hwy 281", "8802 MARBACH RD", "5251 Timberhill", "408 S LBJ Drive", "732 S. Austin St.", "1010 La Salle Dr.", "2314 West Adams Ave", "301 Tanger Dr", "3809 N State Line Ave", "3320 Troup Hwy", "5615 Troup Hwy", "920 Pat Booker Rd", "365 North Main St.", "1427 S. Valley Mills Dr.", "525 S Texas Blvd", "273 West 500 South #6", "1917 W 1800 N", "719 N Main St", "3651 Wall Ave #1072", "340 East 525 North", "3562 Washington Blvd", "391 S Main Street", "4510 S 900 W", "3464 W 4800 S", "1785 South 4130 West", "9860 South 700 East", "8558s 1300e", "1312 East Center Street", "1127 E 1060 N", "271 W 1260 N", "2160 West 4700 South", "3245 W 7800 S", "1100 S Hayes ST", "801 University City Blvd", "14260 B Centreville Square", "390 Hillsdale Drive", "205 S East Street", "764 Westover Drive", "4021 University Drive", "11750 Fair Oaks Mall", "2025 Plank Rd", "1818-G Todds Lane", "205 East Broadway Avenue", "3102 Memorial Ave", "937 Starling Ave", "467 B Denbigh Blvd", "9649 1st View St.", "2862 Airline Blvd", "6112 Lakeside Ave", "7522 Forest Hill Ave", "430A Salem Avenue", "7700 Backlick Rd", "4404 Holland Plaza Shopping Ctr", "410 Lightfoot", "189 Ridgeview Rd SW", "110 N 4th St", "5062 Forte Straede", "457 Main St", "155 Dorset Street", "105 E Heron St", "1431 Railroad Avenue", "630 N Callow Ave", "603 4th St.", "1058 NW State Avenue", "838 6th Street", "1105 Basin ST SW", "1913 Hewitt Ave", "10135 224th ST E", "4230 Pacific Ave", "780 OCEAN BEACH HIGHWAY", "224 Stewart Rd 115", "3500 S. Meridian", "465 Renton Center Way SW", "14020 Aurora Ave N", "616 8TH AVE S", "9414 Ridgetop Blvd NW", "1207 13th St", "2525 E 29th Ave", "4750 N Division St", "20 S. Pines", "15411 1st Ave Ct 5 C113", "5510 6th Ave", "120 E Alder St", "2002 Englewood Avenue", "6 N 3rd street", "808C W Wisconsin Ave", "W3169 Van Roy Rd", "123 3rd Ave", "12714 W Hampton Ave", "635 E Wisconsin St.", "2215 Fairfax Street", "21 N Main St", "65 W Scott St", "2633 Development Dr.", "1683 E. Mason Street", "2160 Ridge Rd", "6120 W Layton Ave", "1441 Plainfield Ave.", "425 Main Street", "4672 Cottage Grove Rd", "326 Main St", "424 Main St E", "9360 State Rd. 16", "408 N. Main Street", "500 Wisconsin Ave", "1204 Minnesota Ave. front", "112 S. Main Street", "1720 Merrill Ave", "8730 W North Ave", "8633 W Greenfield Ave Lower", "606 N Eisenhower Dr", "270 Progress Way", "77 Monroe St", "9515 Mall Road", "35 RHL BLVD", "312 West 17th Street", "1612 Central Avenue", "175 River View Drive", "515 North Front Street",};
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
            if(input == "testFive")
            {
                game.score += 5;
            }
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
    if(score >= 15)
    {
        Console.WriteLine("Nice Play! Thats a lot of points! heres your prize Blue-eyes White Dragon!");
        Console.WriteLine("_______________________\n|   Blue-Eyes White Dragon   |\n|______________________ |\n|  |       _^—-------/  /_  /   ^  |  |\n|  |     (  |		 / ^  |  |\n|  |    (    |  <(/)>             _  ^|  |\n|  |     | 	^ /                   /       |  |\n|  |      ^ /__________ /       |  |\n|  |		|	|      |  |\n|_|___________|______|_ |_|\n|			          |\n|                            	          |\n|			          |\n|                            	          |\n|			       \n|______________________ |");
    }else if(score >= 10)
    {
        Console.WriteLine("Nice! atleast half crorect heres your prize! Pot of greed");
        Console.WriteLine("_______________________\n|  	Pot of greed              |\n|______________________ |\n|  |             _______            |  |\n|  |           /               |           |  |\n|  |         /    (^)    (^)  |==      |  |\n|  |        |  <---------->  |   |     |  |\n|  |         |   [_^_^_]   /==      |  |\n|  |            |______|             |  |\n|_|___________________ |_|\n|			          |\n|                            	          |\n|			          |\n|                            	          \n|			          |\n|______________________ |");
    }else
    {
        Console.WriteLine("Nice try! but you got some learning to do if you want a prize! ");
    }
    localStore();
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
private void localStore()
{
    Console.WriteLine("If you would like to play yugioh in real life enter your zip code and ill tell you a store near you that holds tournaments!");
    string? zipcode = Console.ReadLine();
    for(int i = 0; i <= zipcodes.Length; i++)
    {
        if(zipcodes[i].ToString() == zipcode)
        {
            Console.WriteLine("a store is in your zipcode the adress is: " + locations[i]);
        }
    }
}

}
