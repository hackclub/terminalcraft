import ora from "ora"
import enquirer from "enquirer";
import {selectAudience} from "./audiences.js";

const logContact = (contact) => {
    console.log("- ID: " + contact.id)
    console.log("- Email: " + contact.email)
    console.log("- First Name: " + (contact.first_name ?? "N/A"))
    console.log("- Last Name: " + (contact.last_name ?? "N/A"))
    console.log("- Created At: " + contact.created_at)
    console.log("- Unsubscribed: " + contact.unsubscribed)

}

export default async function({resend, apiKey}) {
    const mainForm = new enquirer.Select({
        message: "Choose an action",
        choices: [
            {name: "add", message: "Add Contact"},
            {name: "retrieve", message: "Retrieve Contact"},
            {name: "update", message: "Update Contact"},
            {name: "delete", message: "Delete Contact"},
            {name: "list", message: "List Contacts"},
        ]
    })
    const mainFormResponse = await mainForm.run()
    switch (mainFormResponse) {
        case "add":
            {
                const audienceID = await selectAudience({resend}, "Choose an audience to add a contact to")
                let form = new enquirer.Form({
                    name: "createContact",
                    message: "Add a contact",
                    choices: [
                        {name: "email", message: "Email"},
                        {name: "firstName", message: "First Name", initial: ""},
                        {name: "lastName", message: "Last Name", initial: ""},
                    ]
                })
                form = await form.run()
                const spin = ora({text: "Adding contact...", spinner: "toggle9"}).start()
                const contact = await resend.contacts.create({
                    audienceId: audienceID,
                    email: form.email,
                    firstName: form.firstName,
                    lastName: form.lastName
                })
                spin.stop()
                //console.log(contact)
                console.log(`Contact with ID ${contact.data.id} added.`)
            }
            break
        case "retrieve":
            {
                const audienceId = await selectAudience({resend}, "Choose an audience")
                let form = new enquirer.Form({
                    name: "retrieveContact",
                    message: "Retrieve a contact",
                    choices: [
                        {name: "emailOrID", message: "Email or Contact ID"},
                    ]
                })
                form = await form.run()
                if (form.emailOrID.includes("@")) {
                    // we need to list contacts and find the contact with the email
                    const spin = ora({text: "Retrieving contact...", spinner: "toggle9"}).start()
                    const contacts = await resend.contacts.list({audienceId})
                    for (let contact of contacts.data.data) {
                        if (contact.email === form.emailOrID) {
                            spin.stop()
                            logContact(contact)
                        }
                    }
                } else {
                    const spin = ora({text: "Retrieving contact...", spinner: "toggle9"}).start()
                    const contact = await resend.contacts.get({id: form.emailOrID, audienceId})
                    spin.stop()
                    console.log("- Email: " + contact.data.email)
                    console.log("- First Name: " + (contact.data.first_name ?? "N/A"))
                    console.log("- Last Name: " + (contact.data.last_name ?? "N/A"))
                    console.log("- Created At: " + contact.data.created_at)
                    console.log("- Unsubscribed: " + contact.data.unsubscribed)
                }
            }
            break
        case "update":
            {
                const audienceId = await selectAudience({resend}, "Choose an audience")
                let form = new enquirer.Form({
                    name: "updateContact",
                    message: "Update a contact",
                    choices: [
                        {name: "emailOrID", message: "Email or Contact ID"},
                        {name: "firstName", message: "First Name", initial: ""},
                        {name: "lastName", message: "Last Name", initial: ""},
                        {name: "unsubscribed", message: "Unsubscribed (either true or false)"}
                    ]
                })
                form = await form.run()
                if (form.emailOrID.includes("@")) {
                    // we need to list contacts and find the contact with the email
                    const spin = ora({text: "Updating contact...", spinner: "toggle9"}).start()
                    const contacts = await resend.contacts.list({audienceId})
                    for (let contact of contacts.data.data) {
                        if (contact.email === form.emailOrID) {
                            const contactUpdate = await resend.contacts.update({
                                id: contact.id,
                                audienceId,
                                firstName: form.firstName,
                                lastName: form.lastName,
                                unsubscribed: form.unsubscribed
                            })
                            spin.stop()
                            console.log(`Contact with ID ${contactUpdate.data.id} updated.`)
                        }
                    }
                } else {
                    const spin = ora({text: "Updating contact...", spinner: "toggle9"}).start()
                    const contactUpdate = await resend.contacts.update({
                        id: form.emailOrID,
                        audienceId,
                        firstName: form.firstName,
                        lastName: form.lastName,
                        unsubscribed: form.unsubscribed
                    })
                    spin.stop()
                    console.log(`Contact with ID ${contactUpdate.data.id} updated.`)
                }
            }
            break
        case "delete":
            {
                const audienceId = await selectAudience({resend}, "Choose an audience")
                let form = new enquirer.Form({
                    name: "deleteContact",
                    message: "Delete a contact",
                    choices: [
                        {name: "emailOrID", message: "Email or Contact ID"},
                    ]
                })
                form = await form.run()
                if (form.emailOrID.includes("@")) {
                    const spin = ora({text: "Deleting contact...", spinner: "toggle9"}).start()
                    const contactDelete = await resend.contacts.remove({email: form.emailOrID, audienceId})
                    spin.stop()
                    console.log(`Contact with ID ${form.emailOrID} deleted.`)
                } else {
                    const spin = ora({text: "Deleting contact...", spinner: "toggle9"}).start()
                    const contactDelete = await resend.contacts.remove({id: form.emailOrID, audienceId})
                    spin.stop()
                    console.log(`Contact with ID ${form.emailOrID} deleted.`)
                }
            }
            break
        case "list":
            {
                const audienceId = await selectAudience({resend}, "Choose an audience")
                const spin = ora({text: "Fetching contacts...", spinner: "toggle9"}).start()
                const contacts = await resend.contacts.list({audienceId})
                spin.stop()
                //show a select with contact names
                const choices = contacts.data.data.map((contact) => {return {message: contact.email, name: contact.id}})
                let answer = new enquirer.Select({
                    name: "listContacts",
                    message: "Choose a contact to view info on",
                    choices
                })
                answer = await answer.run()
                for (let contact of contacts.data.data) {
                    if (contact.id === answer) {
                        logContact(contact)
                    }
                }
            }
    }
    process.exit(0)
}