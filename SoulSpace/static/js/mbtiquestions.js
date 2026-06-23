/*
 * 16 questions extracted from the provided index.js file.
 * Each question has an associated dimension to determine the MBTI type.
 */
const mbtiData = [
    { q: "You enjoy being the center of attention.", dim: ["E", "I"] },
    { q: "You are energized by social gatherings.", dim: ["E", "I"] },
    { q: "You find it easy to approach and talk to new people.", dim: ["E", "I"] },
    { q: "After a busy day, you prefer to recharge alone rather than with others.", dim: ["I", "E"] },

    { q: "You rely more on facts and past experience than theories.", dim: ["S", "N"] },
    { q: "You prefer practical tasks over exploring abstract possibilities.", dim: ["S", "N"] },
    { q: "You focus more on present details than future possibilities.", dim: ["S", "N"] },
    { q: "You enjoy imagining what could be rather than what is.", dim: ["N", "S"] },

    { q: "You make decisions using logic and consistency over empathy.", dim: ["T", "F"] },
    { q: "You value fairness and principles over personal circumstances.", dim: ["T", "F"] },
    { q: "You prioritize harmony and people’s feelings in decisions.", dim: ["F", "T"] },
    { q: "You tend to consider the human impact before the numbers.", dim: ["F", "T"] },

    { q: "You prefer a structured plan over going with the flow.", dim: ["J", "P"] },
    { q: "You like closing tasks early rather than keeping options open.", dim: ["J", "P"] },
    { q: "You are flexible and comfortable adapting plans last minute.", dim: ["P", "J"] },
    { q: "You feel best when your schedule is organized and decided.", dim: ["J", "P"] },
];