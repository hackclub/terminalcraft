import ora from "ora"
import enquirer from "enquirer";
import {selectAudience} from "./audiences.js";
import fs from "fs/promises"

const logEmail = (email) => {
    console.log(`ID: ${email.id}`)
    console.log(`From: ${email.from}`)
    console.log(`To: ${email.to}`)
    console.log(`Subject: ${email.subject}`)
    console.log(`BCC: ${email.bcc}`)
    console.log(`CC: ${email.cc}`)
    console.log(`Reply To: ${email.reply_to}`)
    console.log(`HTML: ${email.html}`)
    console.log(`Text: ${email.text}`)
}

export const addRecipient = async ({resend}, msg) => {
    let method = new enquirer.Select({
        message: (msg) + "Choose a method",
        choices: [
            {name: "manual", message: "Manual Entry"},
            {name: "audience", message: "Send to entire Audience"},
            {name: "none", message: "None"}
        ]
    })
    method = await method.run()
    if (method === "manual") {
        let email = new enquirer.Input({
            message: "Email Addresses, separated by commas",
            initial: "something@someone.co, delivery@resend.com"
        })
        email = await email.run()
        return email.split(",").map((email) => email.trim())
    } else if (method === "audience") {
        const audienceId = await selectAudience({resend}, "Choose an audience")
        const spinner = ora({text: "Retrieving audience...", spinner: "toggle9"}).start()
        const audience = await resend.contacts.list({audienceId})
        spinner.stop()
        // map audience.data.data array into a comma-separated list of email addresses
        return audience.data.data.map((contact) => contact.email)
    } else {
        return []
    }
}

export default async function({resend, apiKey}) {
    let mainForm = new enquirer.Select({
        message: "Choose an action",
        choices: [
            {name: "send", message: "Send Email"},
            {name: "retrieve", message: "Retrieve Email"},
        ]
    })
    mainForm = await mainForm.run()
    switch (mainForm) {
        case "send":
            {
                let from = new enquirer.Input({
                    message: "From",
                    initial: "Acme <onboarding@resend.dev>"
                })
                from = await from.run()
                const to = await addRecipient({resend}, "To: ")
                let subject = new enquirer.Input({
                    message: "Subject",
                    initial: "Changelog | Acne Alpha"
                })
                subject = await subject.run()
                const bcc = await addRecipient({resend}, "BCC: ")
                const cc = await addRecipient({resend}, "CC: ")
                const reply_to = await addRecipient({resend}, "Reply To: ")
                let html = new enquirer.Select({
                    message: "HTML insert method",
                    choices: [
                        {name: "file", message: "From file"},
                        {name: "input", message: "From input"},
                        {name: "none", message: "None (text instead)"}
                    ]
                })
                html = await html.run()
                if (html === "file") {
                    let file = new enquirer.Input({
                        message: "File path"
                    })
                    file = await file.run()
                    html = await fs.readFile(file, "utf8")
                } else if (html === "input") {
                    let htmlInput = new enquirer.Input({
                        message: "HTML",
                        initial: "<h1>This is an email</h1>"
                    })
                    html = await htmlInput.run()
                }
                let text = new enquirer.Input({
                    message: "Text (not required if HTML is provided)",
                    initial: "This is a text email"
                })
                text = await text.run()
                const spinner = ora({text: "Sending email...", spinner: "toggle9"}).start()
                const email = await resend.emails.create({
                    from,
                    to,
                    subject,
                    bcc,
                    cc,
                    reply_to,
                    html,
                    text
                })
                if (email.error) {
                    spinner.stop()
                    console.error(email.error.message)
                    process.exit(1)
                }
                spinner.stop()
                console.log(`Email with ID ${email.data.id} sent.`)
            }
            break
        case "retrieve":
            {
                let emailId = new enquirer.Input({
                    message: "Email ID"
                })
                emailId = await emailId.run()
                const spinner = ora({text: "Retrieving email...", spinner: "toggle9"}).start()
                const email = await resend.emails.get(emailId)
                spinner.stop()
                logEmail(email.data)
            }
    }
}