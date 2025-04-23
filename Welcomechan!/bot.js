const { Client, GatewayIntentBits, REST, Routes, SlashCommandBuilder, InteractionType } = require('discord.js');
const { token, welcomeChannelId, goodbyeChannelId } = require('./config/config');
const guildMemberAdd = require('./events/guildMemberAdd');
const guildMemberRemove = require('./events/guildMemberRemove');

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMembers,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
    ],
});

client.once('ready', async () => {
    console.log(`Logged in as ${client.user.tag}!`);

    // Register the /hi, /credits, and /dice commands
    const rest = new REST({ version: '10' }).setToken(token);
    const commands = [
        new SlashCommandBuilder()
            .setName('hi')
            .setDescription('Say hi to the bot!'),
        new SlashCommandBuilder()
            .setName('credits')
            .setDescription('Show the bot credits!'),
        new SlashCommandBuilder()
            .setName('dice')
            .setDescription('Roll a dice (1-6)!'),
        new SlashCommandBuilder()
            .setName('count')
            .setDescription('Count from 1 to your number!')
            .addIntegerOption(option =>
                option.setName('number')
                    .setDescription('The number to count to')
                    .setRequired(true)
            )
    ];
    try {
        await rest.put(
            Routes.applicationCommands(client.user.id),
            { body: commands.map(cmd => cmd.toJSON()) }
        );
        console.log('Slash commands /hi, /credits, and /dice registered.');
    } catch (error) {
        console.error('Error registering slash commands:', error);
    }
});

client.on('guildMemberAdd', (member) => {
    guildMemberAdd(member, welcomeChannelId);
});

client.on('guildMemberRemove', (member) => {
    guildMemberRemove(member, goodbyeChannelId);
});

client.on('interactionCreate', async (interaction) => {
    if (interaction.type !== InteractionType.ApplicationCommand) return;
    if (interaction.commandName === 'hi') {
        await interaction.reply('Hi! UwU!');
    }
    if (interaction.commandName === 'credits') {
        await interaction.reply('Follow @alexandrospanag on GitHub!');
    }
    if (interaction.commandName === 'dice') {
        const roll = Math.floor(Math.random() * 6) + 1;
        await interaction.reply(`You rolled a: ${roll}`);
    }
    if (interaction.commandName === 'count') {
        const number = interaction.options.getInteger('number');
        if (number > 0) {
            await interaction.reply('Counting:');
            for (let i = 1; i <= number; i++) {
                await interaction.followUp(`${i}`);
            }
        } else {
            await interaction.reply('Please enter a number greater than 0.');
        }
    }
});

client.login(token);