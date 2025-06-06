#!/usr/bin/env node

const https = require("https");
const { Command } = require("commander");

function only() {
    const message = `
    ==========================================================================
    ==========================================================================
    ==========================================================================
    ==========================================================================
    ==========================================================================
    ==========================================================================
    =================++===================================+***+===============
    ==============+%@@@@@*============================+#@@@@@@@#==============
    =============+@@@=+@@@@#========================+%@@@@+  *@@#=============
    =============@@@     +@@@*====================+%@@%-      %@@+============
    ============#@@:       #@@%+================+%@@@         .@@*============
    ===========+@@#         =@@@++#%@@@@@@@@@%#*@@@-           @@%============
    ===========#@@-           @@@@@@%%######%@@@@@             #@@============
    ==========+%@%             =-               .              #@@============
    ==========+@@#                                             %@@============
    ========++%@@#                                             %@@@%+=========
    ======+%@@@@#.                                               -%@@@%+======
    =====#@@@:                                                      -@@@*=====
    ====%@@*                                                          @@@#====
    ===%@@=                 @@@%         .        #@@@                 +@@#===
    ==*@@#                  %@@*       +@@@.      :@@+                  #@@+==
    ==*@@+                                                              -@@#==
    ==*@@+                                                               @@%==
    ==+@@#                            ----==-         :%@@:              @@%==
    ===#@@=                          *@@@@@@@:       -@@%@@+ -%@@@=     :@@#==
    ====%@@=                                         @@# *@@@@@#%@@     *@@*==
    =====#@@#                                        %@@  @@@@  *@%    #@@#===
    ======*@@@+                                       @@= @@%  -@@-  #@@@*====
    ========#@@@@+                                    %@@     -@@@@@@@@#+=====
    =========+*%@@@@@@@#=                           *@@#=      %@@@@*=========
    =============+*#@@@@@+                         :@@-          *@@#=========
    ===============*@@*                            =@@            @@@+========
    ===============%@@.                            :@@%-         %@@#=========
    ==============+@@#                               *@@=      @@@@#==========
    ==============*@@=                                          :@@%+=========
    =============+%@@                                            @@@+=========
    =============+@@@                                            #@@*=========
    =============+@@#                                            =@@*=========
    =============*@@*                                            -@@*=========
    =============*@@+                                            -@@*=========
    `;
    console.log(message);
}

class GitHubStats {
    constructor() {
        this.program = new Command();
        this.setupCommands();
    }

    setupCommands() {
        this.program
            .name("SHATES")
            .version("1.0.0")
            .action(() => {
                only();
            });

        this.program
            .command("user <username>")
            .description("Display user statistics")
            .option("-d, --detailed", "Show detailed analysis")
            .action((username, options) => {
                this.showUserStats(username, options.detailed);
            });

        this.program
            .command("compare <user1> <user2>")
            .description("Compare two users")
            .action((user1, user2) => {
                this.compareUsers(user1, user2);
            });

        this.program
            .command("repos <username>")
            .description("List top repositories")
            .option("-l, --limit <number>", "Number of repos to display", "10")
            .action((username, options) => {
                this.showTopRepos(username, parseInt(options.limit));
            });

        this.program.parse();
    }

    showLoader(message, duration = 2000) {
        return new Promise((resolve) => {
            const frames = ["|", "/", "-", "\\"];
            let i = 0;

            process.stdout.write(`\n${message} `);

            const interval = setInterval(() => {
                process.stdout.write(`\r${message} [${frames[i]}]`);
                i = (i + 1) % frames.length;
            }, 100);

            setTimeout(() => {
                clearInterval(interval);
                process.stdout.write(`\r${message} [COMPLETE]\n`);
                resolve();
            }, duration);
        });
    }

    showProgressBar(message, steps = 20) {
        return new Promise((resolve) => {
            let progress = 0;
            process.stdout.write(`\n${message}\n`);

            const interval = setInterval(() => {
                const filled = Math.floor((progress / 100) * steps);
                const empty = steps - filled;
                const bar =
                    "[" +
                    "=".repeat(filled) +
                    ">".repeat(progress < 100 ? 1 : 0) +
                    " ".repeat(empty - (progress < 100 ? 1 : 0)) +
                    "]";

                process.stdout.write(`\r${bar} ${progress}%`);

                progress += 5;
                if (progress > 100) {
                    clearInterval(interval);
                    process.stdout.write(`\r${bar} 100% DONE\n`);
                    resolve();
                }
            }, 150);
        });
    }

    printBanner() {
        const banner = `
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%+++=-::..:-=+++%@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@#=-:.................-+#--::-+#@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@#==++:..............................:=%@@@@@@@
@@@@@@@@@@@@@@@@@@%-...............................+*-....=#@@@@@@
@@@@@@@@@@@@@@@@@%-..-=.............................++*=:..+#@@@@@
@@@@@@@@@@@@@@@@%+..-++..............................##@@#++@@@@@@
@@@@@@@@@@@@@@@@#:.-%#+....:=:...:::....%@#..........:#@@@@@@@@@@@
@@@@@@@@@@@@@@@@#=+%@#=...-%%:...:##:...:+:::::.......=%@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@%+.:::-#:....=+:....:............-%@@@@@@@@@@
@@@@@@@@@@%%%%%%%%####*===--:.........................-#@@@@@@@@@@
@@@@@@@@-...................:+........................-*@@@@@@@@@@
@@@@@@@%-....................-=.......................-*@@@@@@@@@@
@@@@@@@%-....................:*.......................:*@@@@@@@@@@
@@@@@@@@=.....................#........................*@@@@@@@@@@
@@@@@@@@+:....................++-----------------=+:..-+%%##++++++
::::::::=-....................==::::::::::::::::*:...:+:::::::::::
....::::-=....................:*===-=+=:::-=-:=:.-++=::::.........
.....:::-#####***++++=-:::.....+-+=:-*=::+#%#=+=:=-::::...........
......:::=++++++++++++===+++++====-:::::=#-::-+=++::..............
.......::::::::::::::::::::::::::::::::::=#%*=-:..................
..........::::::::::::::..........................................
..................................................................
.---:+-+++...-+---+=.-:--#=+:..=+.:.--+-:=-...-:--:-..............
.::-====-=:..-=-==--.-==---:..::--=---:=--=:..:-=-:...............
...........:..................................................::..`;
        console.log(banner);
    }

    printHeader(title) {
        const width = 60;
        const padding = Math.max(0, Math.floor((width - title.length) / 2));

        console.log("\n" + "=".repeat(width));
        console.log(
            "=" +
                " ".repeat(padding) +
                title +
                " ".repeat(width - padding - title.length - 2) +
                "=",
        );
        console.log("=".repeat(width));
    }

    printSection(title) {
        console.log(
            `\n--- ${title.toUpperCase()} ${"─".repeat(50 - title.length)}`,
        );
    }

    printBox(content, width = 50) {
        console.log("┌" + "─".repeat(width - 2) + "┐");
        content.forEach((line) => {
            const padding = width - line.length - 4;
            console.log("│ " + line + " ".repeat(Math.max(0, padding)) + " │");
        });
        console.log("└" + "─".repeat(width - 2) + "┘");
    }

    async fetchGitHubData(url) {
        return new Promise((resolve, reject) => {
            const options = {
                headers: {
                    "User-Agent": "gh-stats-terminal-v1.0",
                    Accept: "application/vnd.github.v3+json",
                },
            };

            https
                .get(url, options, (res) => {
                    let data = "";

                    res.on("data", (chunk) => {
                        data += chunk;
                    });

                    res.on("end", () => {
                        if (res.statusCode === 200) {
                            resolve(JSON.parse(data));
                        } else {
                            reject(
                                new Error(
                                    `API ERROR ${res.statusCode}: ${JSON.parse(data).message}`,
                                ),
                            );
                        }
                    });
                })
                .on("error", (err) => {
                    reject(err);
                });
        });
    }

    async showUserStats(username, detailed = false) {
        try {
            this.printBanner();
            this.printHeader("GITHUB USER ANALYSIS");

            await this.showLoader("CONNECTING TO GITHUB API", 1500);
            await this.showProgressBar("DOWNLOADING USER DATA", 25);

            const user = await this.fetchGitHubData(
                `https://api.github.com/users/${username}`,
            );

            this.displayUserInfo(user, detailed);

            if (detailed) {
                await this.showLoader("ANALYZING REPOSITORIES", 2000);
                await this.showAdditionalStats(username);
            }
        } catch (error) {
            console.log(`\nERROR: ${error.message}`);
            console.log("SYSTEM HALTED");
        }
    }

    displayUserInfo(user, detailed) {
        this.printSection("USER PROFILE");

        const profileData = [
            `USERNAME: ${user.login}`,
            `FULL NAME: ${user.name || "N/A"}`,
            `PROFILE: ${user.html_url}`,
            user.bio ? `BIO: ${user.bio}` : null,
            user.location ? `LOCATION: ${user.location}` : null,
            user.company ? `COMPANY: ${user.company}` : null,
        ].filter(Boolean);

        this.printBox(profileData);

        this.printSection("STATISTICS");

        const stats = [
            `PUBLIC REPOSITORIES.....: ${user.public_repos}`,
            `FOLLOWERS...............: ${user.followers}`,
            `FOLLOWING...............: ${user.following}`,
            `PUBLIC GISTS............: ${user.public_gists}`,
            `ACCOUNT CREATED.........: ${new Date(user.created_at).toLocaleDateString()}`,
        ];

        if (detailed) {
            stats.push(
                `LAST UPDATED............: ${new Date(user.updated_at).toLocaleDateString()}`,
            );
        }

        this.printBox(stats, 55);
    }

    async showAdditionalStats(username) {
        try {
            const repos = await this.fetchGitHubData(
                `https://api.github.com/users/${username}/repos?per_page=100`,
            );

            const languages = {};
            let totalStars = 0;
            let totalForks = 0;

            repos.forEach((repo) => {
                if (repo.language) {
                    languages[repo.language] =
                        (languages[repo.language] || 0) + 1;
                }
                totalStars += repo.stargazers_count;
                totalForks += repo.forks_count;
            });

            this.printSection("ADVANCED METRICS");

            const metrics = [
                `TOTAL STARS.............: ${totalStars}`,
                `TOTAL FORKS.............: ${totalForks}`,
                `REPOSITORIES ANALYZED...: ${repos.length}`,
            ];

            this.printBox(metrics, 55);

            const topLanguages = Object.entries(languages)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 5);

            if (topLanguages.length > 0) {
                this.printSection("PROGRAMMING LANGUAGES");

                const langData = topLanguages.map(
                    ([lang, count]) =>
                        `${lang.padEnd(15, ".")}: ${count} REPOS`,
                );

                this.printBox(langData, 45);
            }
        } catch (error) {
            console.log(`\nWARNING: Could not fetch additional statistics`);
            console.log(`REASON: ${error.message}`);
        }
    }

    async compareUsers(user1, user2) {
        try {
            this.printBanner();
            this.printHeader("USER COMPARISON SYSTEM");

            await this.showLoader("INITIALIZING COMPARISON MODULE", 1000);
            await this.showProgressBar("FETCHING USER DATA", 30);

            const [userData1, userData2] = await Promise.all([
                this.fetchGitHubData(`https://api.github.com/users/${user1}`),
                this.fetchGitHubData(`https://api.github.com/users/${user2}`),
            ]);

            this.displayComparison(userData1, userData2);
        } catch (error) {
            console.log(`\nCOMPARISON FAILED: ${error.message}`);
        }
    }

    displayComparison(user1, user2) {
        this.printSection(
            `${user1.login.toUpperCase()} VS ${user2.login.toUpperCase()}`,
        );

        const metrics = [
            { label: "PUBLIC REPOSITORIES", key: "public_repos" },
            { label: "FOLLOWERS", key: "followers" },
            { label: "FOLLOWING", key: "following" },
            { label: "PUBLIC GISTS", key: "public_gists" },
        ];

        metrics.forEach((metric) => {
            const val1 = user1[metric.key];
            const val2 = user2[metric.key];
            const winner =
                val1 > val2 ? user1.login : val2 > val1 ? user2.login : "TIE";

            console.log(`\n${metric.label}:`);
            console.log(`├─ ${user1.login.padEnd(15, ".")}: ${val1}`);
            console.log(`├─ ${user2.login.padEnd(15, ".")}: ${val2}`);
            console.log(
                `└─ WINNER..................: ${winner === "TIE" ? "DRAW" : winner.toUpperCase()}`,
            );
        });


        const created1 = new Date(user1.created_at);
        const created2 = new Date(user2.created_at);
        const older = created1 < created2 ? user1.login : user2.login;

        console.log(`\nACCOUNT AGE:`);
        console.log(
            `├─ ${user1.login.padEnd(15, ".")}: ${created1.toLocaleDateString()}`,
        );
        console.log(
            `├─ ${user2.login.padEnd(15, ".")}: ${created2.toLocaleDateString()}`,
        );
        console.log(`└─ OLDER ACCOUNT...........: ${older.toUpperCase()}`);

        console.log("\n" + "=".repeat(60));
        console.log("COMPARISON ANALYSIS COMPLETE");
        console.log("=".repeat(60));
    }

    async showTopRepos(username, limit) {
        try {
            this.printBanner();
            this.printHeader("REPOSITORY ANALYSIS");

            await this.showLoader("SCANNING REPOSITORIES", 1500);
            await this.showProgressBar("SORTING BY POPULARITY", 25);

            const repos = await this.fetchGitHubData(
                `https://api.github.com/users/${username}/repos?per_page=100&sort=stars`,
            );

            const topRepos = repos
                .sort((a, b) => b.stargazers_count - a.stargazers_count)
                .slice(0, limit);

            if (topRepos.length === 0) {
                console.log(
                    `\nNO PUBLIC REPOSITORIES FOUND FOR USER: ${username}`,
                );
                return;
            }

            this.printSection(`TOP ${topRepos.length} REPOSITORIES`);

            topRepos.forEach((repo, index) => {
                console.log(
                    `\n[${(index + 1).toString().padStart(2, "0")}] ${repo.name.toUpperCase()}`,
                );
                console.log(
                    "├─ STARS...................: " + repo.stargazers_count,
                );
                console.log("├─ FORKS...................: " + repo.forks_count);
                console.log(
                    "├─ LANGUAGE................: " +
                        (repo.language || "NOT SPECIFIED"),
                );
                console.log(
                    "├─ DESCRIPTION.............: " +
                        (repo.description || "NO DESCRIPTION").substring(0, 50),
                );
                console.log("└─ URL.....................: " + repo.html_url);
            });

            console.log("\n" + "=".repeat(60));
            console.log("REPOSITORY SCAN COMPLETE");
            console.log("=".repeat(60));
        } catch (error) {
            console.log(`\nREPOSITORY SCAN FAILED: ${error.message}`);
        }
    }

    run() {
        if (process.argv.length === 2) {
            console.log("\nGITHUB STATISTICS TERMINAL v1.0");
            console.log("================================");
            console.log("SYSTEM READY FOR INPUT");
            console.log("TYPE --help FOR AVAILABLE COMMANDS");
            this.program.help();
        }
    }
}


const cli = new GitHubStats();
cli.run();
