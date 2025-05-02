
const spawnEnemy = () => {
const enemyZone = document.getElementById('enemy-zone');
enemyZone.innerHTML = '';
const enemy = document.createElement('div');
enemy.className = 'absolute bottom-8 right-12 bg-red-600 text-white text-xs px-3 py-1 rounded-full animate-bounce shadow-lg';
enemy.textContent = '⚔️ Enemy Appeared!';
enemyZone.appendChild(enemy);
setTimeout(() => enemy.remove(), 5000);
};
document.getElementById('explore-btn').addEventListener('click', spawnEnemy);

