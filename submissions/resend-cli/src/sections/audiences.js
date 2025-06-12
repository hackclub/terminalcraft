import ora from "ora"
import enquirer from "enquirer";

const logAudience = (audience) => {
    console.log(`- ID: ${audience.id}`)
    console.log(`- Name: ${audience.name}`)
    if (audience.created_at) {
        console.log(`- Created At: ${audience.created_at}`)
    }
}

export default async function({resend, apiKey}) {
    let mainForm = new enquirer.Select({
        message: "Choose an action",
        choices: [
            {name: "add", message: "Add Audience"},
            {name: "retrieve", message: "List/Retrieve Audience"},
            {name: "delete", message: "Delete Audience"},
        ]
    })
    mainForm = await mainForm.run()

    switch (mainForm) {
        case "add":
            {
                let form = new enquirer.Form({
                    name: "createAudience",
                    message: "Create an audience",
                    choices: [
                        {name: "name", message: "Name", initial: "My Audience"},
                    ]
                })
                form = await form.run()
                const spinner = ora({text: "Creating audience...", spinner: "toggle9"}).start()
                const audience = await resend.audiences.create({name: form.name})
                spinner.stop()
                console.log(`Audience created.`)
                logAudience(audience.data)
            }
            break
        case "retrieve":
            {
                const audienceId = await selectAudience({resend}, "Choose an audience")
                const spinner = ora({text: "Retrieving audience...", spinner: "toggle9"}).start()
                const audience = await resend.audiences.get(audienceId)
                spinner.stop()
                console.log(`Audience '${audience.data.name}' retrieved.`)
                logAudience(audience.data)
            }
            break
        case "delete":
            {
                const audienceId = await selectAudience({resend}, "Choose an audience")
                let confirmation = new enquirer.Confirm({
                    message: "Are you sure you want to delete this audience?",
                    initial: false
                })
                confirmation = await confirmation.run()
                if (!confirmation) {
                    console.log("Cancelled.")
                    process.exit(0)
                }
                const spinner = ora({text: "Deleting audience...", spinner: "toggle9"}).start()
                await resend.audiences.remove(audienceId)
                spinner.stop()
                console.log("Audience deleted.")
            }
            break
    }
}

export async function selectAudience({resend}, message) {
    const spinner = ora({text: "Fetching audiences...", spinner: "toggle9"}).start()
    const audiences = await resend.audiences.list()
    spinner.stop()
    const choices = audiences.data.data.map((audience) => {return {message: audience.name, name: audience.id}})
    let answer = new enquirer.Select({
        name: "listAudiences",
        message: message ?? "Choose an audience",
        choices
    })
    answer = await answer.run()
    return answer
}