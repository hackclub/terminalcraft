import ora from "ora"
import enquirer from "enquirer";

const logAPIKey = (apiKey) => {
    console.log("- ID: " + apiKey.id)
    if (apiKey.token) {
        console.log("- API Key: " + apiKey.token)
    }
    if (apiKey.name) {
        console.log("- Name: " + apiKey.name)
    }
    if (apiKey.created_at) {
        console.log("- Created At: " + apiKey.created_at)
    }
}

export default async function({resend}, apiKey) {
    const prompt = new enquirer.Select({
        message: "Choose an action",
        choices: [
            {name: "create", message: "Create API Key"},
            {name: "list", message: "List API Keys"},
            {name: "delete", message: "Delete API Key"},
        ]
    })
    const answer = await prompt.run()
    switch (answer) {
        case "create":
            {
                let form = new enquirer.Form({
                    name: "createApiKey",
                    message: "Create an API Key.\nPossible values for permission: full, sending.",
                    choices: [
                        {name: "name", message: "Name", initial: "My API Key"},
                        {name: "permission", message: "Permission", initial: "full"}
                    ]
                })
                form = await form.run()
                const name = form.name
                const permission = form.permission === "sending" ? "sending_access" : "full_access"
                const spinner = ora({text: "Creating API Key...", spinner: "toggle9"}).start()
                const apiKey = await resend.apiKeys.create({name, permission})
                spinner.stop()
                console.log("IMPORTANT! Save this API key in a safe place. It will not be shown again.")
                logAPIKey(apiKey.data)
            }
            break;
        case "list":
            {
                const spinner2 = ora({text: "Fetching API Keys...", spinner: "toggle9"}).start()
                const listApiKeysResponse = await resend.apiKeys.list()
                spinner2.stop()
                const choices = listApiKeysResponse.data.data.map((apiKey) => {
                    return {message: apiKey.name, name: apiKey.id}
                })
                //console.log(choices)
                let answer = new enquirer.Select({
                    name: "listApiKeys",
                    message: "Choose an API Key to view info on",
                    choices
                })
                answer = await answer.run()
                for (let apiKey of listApiKeysResponse.data.data) {
                    if (apiKey.id === answer) {
                        logAPIKey(apiKey)
                    }
                }
            }
            break
        case "delete":
            {
                const spinner3 = ora({text: "Fetching API Keys...", spinner: "toggle9"}).start()
                const listApiKeysResponse2 = await resend.apiKeys.list()
                spinner3.stop()
                const choices2 = listApiKeysResponse2.data.data.map((apiKey) => {return {message: apiKey.name, name: apiKey.id}})
                let answer2 = new enquirer.Select({
                    name: "deleteApiKey",
                    message: "Choose an API Key to delete",
                    choices: choices2
                })
                answer2 = await answer2.run()
                console.log(answer2)
                let confirmDelete = new enquirer.Confirm({
                    message: "If this API Key is the one you make resend-cli with, you will not be able to use resend-cli anymore with the same key. This action is IRREVERSIBLE!!"
                })
                confirmDelete = await confirmDelete.run()
                if (!confirmDelete) {
                    console.log("Aborting...")
                    process.exit(0)
                }
                const spinner4 = ora({text: "Deleting API Key...", spinner: "toggle9"}).start()
                await resend.apiKeys.remove(answer2)
                spinner4.stop()
                    console.log("API Key deleted.")
            }
            break
    }
    process.exit(0)
}