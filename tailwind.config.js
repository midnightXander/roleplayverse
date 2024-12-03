module.exports = {
    mode: 'jit',
    content: [
        './core/templates/core/**/*.{html,js}',
        './battles/templates/battles/**/*.{html,js}',
        './chat/templates/chat/**/*.{html,js}',
        './events/templates/events/**/*.{html,js}',
        './characters/templates/characters/**/*.{html,js}',
        './users/templates/users/**/*.{html,js}',
        './blog/templates/blog/**/*.{html,js}',
        './moderator/templates/moderator/**/*.{html,js}',


    ],
    theme:{
        extend:{},
    },
    variants:{},
    plugins:[],
}