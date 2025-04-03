import ora from "ora"
import enquirer from "enquirer";

const logDomain = (domain) => {
    console.log(`ID: ${domain.data.id}`)
    console.log(`Name: ${domain.data.name}`)
    console.log(`Region: ${domain.data.region}`)
    console.log(`Status: ${domain.data.status}`)
    console.log(`Created At: ${domain.data.created_at}`)
}

export default async function({resend}) {
    let mainForm = new enquirer.Select({
        message: "Choose an action",
        choices: [
            {name: "add", message: "Add Domain"},
            {name: "retrieve", message: "Retrieve Domain"},
            {name: "verify", message: "Verify Domain"},
            {name: "update", message: "Update Domain"},
            {name: "list", message: "List Domains"},
            {name: "delete", message: "Delete Domain"},
        ]
    })
    mainForm = await mainForm.run()
    switch (mainForm) {
        case "add":
            {
                let form = new enquirer.Form({
                    name: "createDomain",
                    message: "Add a domain",
                    choices: [
                        {name: "name", message: "Domain/subdomain without http"},
                        {name: "region", message: "Region (possible values: us-east-1, eu-west-1, sa-east-1, ap-northeast-1)", initial: "us-east-1"},
                    ]
                })
                form = await form.run()
                const spin = ora({text: "Adding domain...", spinner: "toggle9"}).start()
                const domain = await resend.domains.create({
                    name: form.name,
                    region: form.region
                })
                if (domain.error) {
                    spin.stop()
                    console.error(domain.error.message)
                    process.exit(1)
                }
                spin.stop()
                console.log(`Domain with ID ${domain.data.id} added.`)

                const choices = domain.data.records.map((record, i) => { return {name: i, message: `Record #${i+1}`} })

                const records = new enquirer.Select({
                    name: "createRecords",
                    message: "Add all of the following records to your DNS provider",
                    choices
                })
                let recordsResult
                async function iterateRecords() {
                    recordsResult = await records.run()
                    let record = domain.data.records[recordsResult]
                    console.log("Add the following record to your DNS provider:")
                    console.log(`- Type: ${record.type}`)
                    console.log(`- Value: ${record.value}`)
                    if (record.priority) {
                        console.log(`- Priority: ${record.priority}`)
                    }
                    if (record.ttl) {
                        console.log(`- TTL: ${record.ttl}`)
                    }
                    console.log("Once you have finished adding the records, run resend-cli and navigate to Domains -> Verify Domain.")
                    await iterateRecords()
                }
                await iterateRecords()
            }
            break
        case "retrieve":
            {
                let form = new enquirer.Form({
                    name: "retrieveDomain",
                    message: "Retrieve a domain",
                    choices: [{name: "id", message: "Domain ID"},]
                })
                form = await form.run()
                const spin = ora({text: "Retrieving domain...", spinner: "toggle9"}).start()
                const domain = await resend.domains.get(form.id)
                if (domain.error) {
                    spin.stop()
                    console.error(domain.error.message)
                    process.exit(1)
                }
                spin.stop()
                logDomain(domain)
            }
            break
        case "verify":
            {
                let form = new enquirer.Form({
                    name: "verifyDomain",
                    message: "Verify a domain",
                    choices: [{name: "id", message: "Domain ID"},]
                })
                form = await form.run()
                const spin = ora({text: "Submitting request...", spinner: "toggle9"}).start()
                const domain = await resend.domains.verify(form.id)
                if (domain.error) {
                    spin.stop()
                    console.error(domain.error.message)
                    process.exit(1)
                }
                spin.stop()
                console.log(`Domain with ID ${domain.data.id} submitted for verification.`)
            }
            break
        case "update":
            {
                let id = new enquirer.Input({
                    message: "Enter the ID of the domain you want to update"
                })
                id = await id.run()
                let confirm1 = new enquirer.Confirm({
                    message: "Enable click tracking?",
                    initial: false
                })
                confirm1 = await confirm1.run()
                let confirm2 = new enquirer.Confirm({
                    message: "Enable open tracking?",
                    initial: false
                })
                confirm2 = await confirm2.run()

                const spin = ora({text: "Updating domain...", spinner: "toggle9"}).start()
                const domain = await resend.domains.update({
                    id,
                    clickTracking: confirm1,
                    openTracking: confirm2
                })
                if (domain.error) {
                    spin.stop()
                    console.error(domain.error.message)
                    process.exit(1)
                }
                spin.stop()
                console.log(`Domain with ID ${domain.data.id} updated.`)
            }
            break
        case "list":
            {
                const spin = ora({text: "Fetching domains...", spinner: "toggle9"}).start()
                const domains = await resend.domains.list()
                if (domains.error) {
                    spin.stop()
                    console.error(domains.error.message)
                    process.exit(1)
                }
                spin.stop()
                const choices = domains.data.data.map((domain) => {return {message: domain.name, name: domain.id}})
                let answer = new enquirer.Select({
                    name: "listDomains",
                    message: "Choose a domain",
                    choices
                })
                answer = await answer.run()
                const domain = await resend.domains.get(answer)
                logDomain(domain)
            }
            break
        case "delete":
            {
                let form = new enquirer.Form({
                    name: "deleteDomain",
                    message: "Delete a domain",
                    choices: [{name: "id", message: "Domain ID"},]
                })
                form = await form.run()
                let confirm = new enquirer.Confirm({
                    message: "Are you sure you want to delete this domain?",
                    initial: false
                })
                confirm = await confirm.run()
                if (!confirm) {
                    console.log("Cancelled.")
                    process.exit(0)
                }
                const spin = ora({text: "Deleting domain...", spinner: "toggle9"}).start()
                const domain = await resend.domains.remove(form.id)
                if (domain.error) {
                    spin.stop()
                    console.error(domain.error.message)
                    process.exit(1)
                }
                spin.stop()
                console.log(`Domain with ID ${form.id} deleted.`)
            }
    }
}