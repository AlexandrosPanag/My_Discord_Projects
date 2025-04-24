const {
    Client,
    GatewayIntentBits,
    REST,
    Routes,
    SlashCommandBuilder,
    InteractionType,
    PermissionsBitField,
} = require("discord.js");
const { token, welcomeChannelId, goodbyeChannelId } = require("./config/config");
const guildMemberAdd = require("./events/guildMemberAdd");
const guildMemberRemove = require("./events/guildMemberRemove");

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMembers,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
    ],
});

// Counting game state
let countingChannelId = null;
let currentCount = 0;
let lastUserId = null;

client.once("ready", async () => {
    console.log(`Logged in as ${client.user.tag}!`);

    // Use guild commands for instant update during development
    const GUILD_ID = '1351673459545079949'; // <-- Replace with your server's ID for instant updates

    const commands = [
        new SlashCommandBuilder().setName("hi").setDescription("Say hi to the bot!"),
        new SlashCommandBuilder().setName("credits").setDescription("Show the bot credits!"),
        new SlashCommandBuilder().setName("dice").setDescription("Roll a dice (1-6)!"),
        new SlashCommandBuilder().setName("2dice").setDescription("Roll two dice (1-6 each)!"),
        new SlashCommandBuilder()
            .setName("count")
            .setDescription("Count from 1 to your number!")
            .addIntegerOption(option =>
                option.setName("number").setDescription("The number to count to").setRequired(true)
            ),
        new SlashCommandBuilder()
            .setName("purge")
            .setDescription("Delete a number of recent messages.")
            .addIntegerOption(option =>
                option.setName("amount").setDescription("Number of messages to delete (2-100)").setRequired(true)
            ),
        new SlashCommandBuilder()
            .setName("kick")
            .setDescription("Kick a user from the server.")
            .addUserOption(option =>
                option.setName("target").setDescription("The user to kick").setRequired(true)
            )
            .addStringOption(option =>
                option.setName("reason").setDescription("Reason for kick").setRequired(false)
            ),
        new SlashCommandBuilder().setName("cat").setDescription("Send a random cat gif!"),
        new SlashCommandBuilder().setName("pun").setDescription("Send a random pun!"),
        new SlashCommandBuilder().setName("countingsetup").setDescription("Setup counting game in this channel."),
    ];

    const rest = new REST({ version: "10" }).setToken(token);
    try {
        await rest.put(
            // Use applicationGuildCommands for instant update, or applicationCommands for global
            Routes.applicationGuildCommands(client.user.id, GUILD_ID),
            { body: commands.map(cmd => cmd.toJSON()) }
        );
        console.log("Slash commands registered!");
    } catch (error) {
        console.error("Error registering slash commands:", error);
    }
});

client.on("guildMemberAdd", (member) => {
    guildMemberAdd(member, welcomeChannelId);
});

client.on("guildMemberRemove", (member) => {
    guildMemberRemove(member, goodbyeChannelId);
});

client.on("interactionCreate", async (interaction) => {
    if (!interaction.isChatInputCommand()) return;

    switch (interaction.commandName) {
        case "hi":
            await interaction.reply(`Hi, ${interaction.user.username}! UwU!`);
            break;
        case "credits":
            await interaction.reply("Follow @alexandrospanag on GitHub!");
            break;
        case "dice":
            await interaction.reply(`You rolled a: ${Math.floor(Math.random() * 6) + 1}`);
            break;
        case "2dice":
            await interaction.reply(
                `You rolled: ${Math.floor(Math.random() * 6) + 1} and ${Math.floor(Math.random() * 6) + 1}`
            );
            break;
        case "count":
            {
                const number = interaction.options.getInteger("number");
                if (number > 0) {
                    await interaction.reply("Counting:");
                    for (let i = 1; i <= number; i++) {
                        await interaction.followUp(`${i}`);
                    }
                } else {
                    await interaction.reply("Please enter a number greater than 0.");
                }
            }
            break;
        case "purge":
            {
                const amount = interaction.options.getInteger("amount");
                if (!interaction.member.permissions.has(PermissionsBitField.Flags.ManageMessages)) {
                    await interaction.reply({ content: "You need the Manage Messages permission to use this command.", ephemeral: true });
                    return;
                }
                if (amount < 2 || amount > 100) {
                    await interaction.reply({ content: "Please enter a number between 2 and 100.", ephemeral: true });
                    return;
                }
                await interaction.deferReply({ ephemeral: true });
                try {
                    const messages = await interaction.channel.bulkDelete(amount, true);
                    await interaction.editReply({ content: `Deleted ${messages.size} messages.` });
                } catch (err) {
                    await interaction.editReply({ content: "Failed to delete messages. Make sure I have permission and the messages are not older than 14 days." });
                }
            }
            break;
        case "kick":
            {
                if (!interaction.member.permissions.has(PermissionsBitField.Flags.KickMembers)) {
                    await interaction.reply({ content: "You need the Kick Members permission to use this command.", ephemeral: true });
                    return;
                }
                const target = interaction.options.getUser("target");
                const reason = interaction.options.getString("reason") || "No reason provided";
                const member = interaction.guild.members.cache.get(target.id);
                if (!member) {
                    await interaction.reply({ content: "User not found in this server.", ephemeral: true });
                    return;
                }
                if (!member.kickable) {
                    await interaction.reply({ content: "I cannot kick this user.", ephemeral: true });
                    return;
                }
                await member.kick(reason);
                await interaction.reply({ content: `Kicked ${target.tag}. Reason: ${reason}` });
            }
            break;
        case "cat":
            {
                const catGifs = [
                    "https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif",
                    "https://media.giphy.com/media/mlvseq9yvZhba/giphy.gif",
                    "https://media.giphy.com/media/13borq7Zo2kulO/giphy.gif",
                    "https://media.giphy.com/media/v6aOjy0Qo1fIA/giphy.gif",
                    "https://media.giphy.com/media/3oriO0OEd9QIDdllqo/giphy.gif",
                ];
                const randomGif = catGifs[Math.floor(Math.random() * catGifs.length)];
                await interaction.reply(randomGif);
            }
            break;
        case "pun":
            {
                const puns = [
                    "I'm reading a book on anti-gravity. It's impossible to put down!",
                    "Did you hear about the mathematician who’s afraid of negative numbers? He’ll stop at nothing to avoid them.",
                    "Why don’t skeletons fight each other? They don’t have the guts.",
                    "I would tell you a joke about construction, but I’m still working on it.",
                    "Why did the scarecrow win an award? Because he was outstanding in his field!",
                    "I used to play piano by ear, but now I use my hands.",
                    "What do you call fake spaghetti? An impasta!",
                    "Why did the bicycle fall over? Because it was two-tired!",
                    "I’m on a seafood diet. I see food and I eat it.",
                    "Why can’t you hear a pterodactyl go to the bathroom? Because the ‘P’ is silent.",
                ];
                const randomPun = puns[Math.floor(Math.random() * puns.length)];
                await interaction.reply(randomPun);
            }
            break;
        case "countingsetup":
            countingChannelId = interaction.channel.id;
            currentCount = 0;
            lastUserId = null;
            await interaction.reply("Counting game started! The next number is 1.");
            break;
    }
});

// Counting game message handler
client.on("messageCreate", async (message) => {
    if (
        countingChannelId &&
        message.channel.id === countingChannelId &&
        !message.author.bot
    ) {
        const expected = currentCount + 1;
        if (
            message.content.trim() === expected.toString() &&
            message.author.id !== lastUserId
        ) {
            currentCount++;
            lastUserId = message.author.id;
            await message.react("✅");
        } else {
            await message.channel.send(
                `❌ ${message.author} ruined the count at ${currentCount}. The next number is 1.`
            );
            currentCount = 0;
            lastUserId = null;
        }
    }
});

client.login(token);
