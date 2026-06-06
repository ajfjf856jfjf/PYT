/**
 * MONDE 1 — NEO CITY 🌆
 * Générateur de monde 3D futuriste avec architecture immersive
 * Basé sur les images de concept art fourni
 */

class NeoCity {
  constructor(scene) {
    this.scene = scene;
    this.buildings = [];
    this.lights = [];
    this.particles = [];
    this.ground = null;
    this.skybox = null;
    this.fogColor = 0x020810;
    this.fogDistance = 800;
    
    // Configuration Neo City
    this.config = {
      buildingGridSize: 60,
      buildingSpacing: 80,
      gridCount: 8,
      coreHeight: 200,
      neonColors: [
        0x00aaff, // Bleu cyan
        0xff00ff, // Magenta
        0x00ff88, // Vert néon
        0xffaa00, // Orange
        0xff0066, // Rose
        0x00ddff  // Bleu clair
      ]
    };
    
    this.initialize();
  }

  initialize() {
    this.createGround();
    this.createSkybox();
    this.createBuildings();
    this.createCoreBuildingCenter();
    this.createStreetLights();
    this.createParticleEffects();
    this.createFloatingElements();
    this.setupLighting();
  }

  // ====== GROUND ======
  createGround() {
    const groundSize = 1000;
    const groundGeometry = new THREE.PlaneGeometry(groundSize, groundSize);
    
    // Créer un canvas texture pour le sol avec motif futuriste
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    
    // Fond noir
    ctx.fillStyle = '#0a0e1a';
    ctx.fillRect(0, 0, 512, 512);
    
    // Motif grille cyberpunk
    ctx.strokeStyle = '#00aaff';
    ctx.lineWidth = 1;
    for (let i = 0; i < 512; i += 32) {
      ctx.beginPath();
      ctx.moveTo(i, 0);
      ctx.lineTo(i, 512);
      ctx.stroke();
      
      ctx.beginPath();
      ctx.moveTo(0, i);
      ctx.lineTo(512, i);
      ctx.stroke();
    }
    
    // Points de grille lumineux
    ctx.fillStyle = '#00aaff';
    for (let i = 0; i < 512; i += 32) {
      for (let j = 0; j < 512; j += 32) {
        ctx.beginPath();
        ctx.arc(i, j, 2, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    
    const texture = new THREE.CanvasTexture(canvas);
    texture.repeat.set(4, 4);
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    
    const material = new THREE.MeshPhongMaterial({
      map: texture,
      color: 0x0a0e1a,
      emissive: 0x002255,
      emissiveIntensity: 0.3
    });
    
    this.ground = new THREE.Mesh(groundGeometry, material);
    this.ground.rotation.x = -Math.PI / 2;
    this.ground.position.y = 0;
    this.ground.receiveShadow = true;
    this.scene.add(this.ground);
  }

  // ====== SKYBOX ======
  createSkybox() {
    // Skybox avec gradient de minuit futuriste
    const skyGeometry = new THREE.SphereGeometry(2000, 32, 32);
    
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    
    // Gradient vertical
    const gradient = ctx.createLinearGradient(0, 0, 0, 512);
    gradient.addColorStop(0, '#000005');      // Noir haut
    gradient.addColorStop(0.3, '#0a0f2e');
    gradient.addColorStop(0.6, '#1a1f4e');
    gradient.addColorStop(1, '#020810');      // Noir bas
    
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 512, 512);
    
    // Ajouter des "étoiles" filaires
    ctx.strokeStyle = 'rgba(0, 170, 255, 0.4)';
    ctx.lineWidth = 0.5;
    for (let i = 0; i < 100; i++) {
      const x = Math.random() * 512;
      const y = Math.random() * 512;
      const size = Math.random() * 2;
      ctx.beginPath();
      ctx.arc(x, y, size, 0, Math.PI * 2);
      ctx.stroke();
    }
    
    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.MeshBasicMaterial({ map: texture, side: THREE.BackSide });
    this.skybox = new THREE.Mesh(skyGeometry, material);
    this.scene.add(this.skybox);
  }

  // ====== BÂTIMENTS ======
  createBuildings() {
    const { buildingGridSize, buildingSpacing, gridCount } = this.config;
    const centerOffset = (gridCount * buildingSpacing) / 2;
    
    for (let x = 0; x < gridCount; x++) {
      for (let z = 0; z < gridCount; z++) {
        const posX = x * buildingSpacing - centerOffset;
        const posZ = z * buildingSpacing - centerOffset;
        
        // Éviter le centre (réservé pour le bâtiment central)
        if (Math.abs(posX) < buildingSpacing && Math.abs(posZ) < buildingSpacing) continue;
        
        const height = 60 + Math.random() * 120;
        const building = this.createBuilding(posX, posZ, height);
        this.buildings.push(building);
      }
    }
  }

  createBuilding(x, z, height) {
    const width = 40 + Math.random() * 30;
    const depth = 40 + Math.random() * 30;
    
    // Corps du bâtiment
    const geometry = new THREE.BoxGeometry(width, height, depth);
    
    // Matériau avec couleur aléatoire
    const neonColor = this.config.neonColors[Math.floor(Math.random() * this.config.neonColors.length)];
    const material = new THREE.MeshPhongMaterial({
      color: 0x1a2a4a,
      emissive: neonColor,
      emissiveIntensity: 0.3,
      shininess: 100
    });
    
    const building = new THREE.Mesh(geometry, material);
    building.position.set(x, height / 2, z);
    building.castShadow = true;
    building.receiveShadow = true;
    
    // Ajouter les fenêtres (utiliser une texture ou des objets)
    this.addWindowsToBuilding(building, width, height, depth, neonColor);
    
    // Détails architecturaux
    this.addBuildingDetails(building, width, height, depth);
    
    this.scene.add(building);
    return building;
  }

  addWindowsToBuilding(building, width, height, depth, neonColor) {
    const windowSize = 6;
    const spacing = 12;
    
    // Fenêtres avant (Z+)
    const windowsPerRow = Math.floor(width / spacing);
    const windowRows = Math.floor(height / spacing);
    
    for (let row = 0; row < windowRows; row++) {
      for (let col = 0; col < windowsPerRow; col++) {
        const x = -width / 2 + col * spacing + spacing / 2;
        const y = -height / 2 + row * spacing + spacing / 2;
        
        // 70% chance une fenêtre soit allumée
        if (Math.random() > 0.3) {
          const windowGeo = new THREE.PlaneGeometry(windowSize, windowSize);
          const windowMat = new THREE.MeshBasicMaterial({
            color: neonColor,
            emissive: neonColor,
            emissiveIntensity: 0.8
          });
          const window = new THREE.Mesh(windowGeo, windowMat);
          window.position.set(x, y, depth / 2 + 0.1);
          building.add(window);
        }
      }
    }
  }

  addBuildingDetails(building, width, height, depth) {
    // Antennes/Détails sur le toit
    if (Math.random() > 0.5) {
      const antennaGeo = new THREE.CylinderGeometry(1, 1, 30, 8);
      const antennaMat = new THREE.MeshPhongMaterial({ color: 0xff00ff, emissive: 0xff00ff, emissiveIntensity: 0.5 });
      const antenna = new THREE.Mesh(antennaGeo, antennaMat);
      antenna.position.set(0, height / 2 + 15, 0);
      antenna.castShadow = true;
      building.add(antenna);
    }
  }

  // ====== BÂTIMENT CENTRAL ======
  createCoreBuildingCenter() {
    const coreHeight = this.config.coreHeight;
    const coreWidth = 80;
    
    // Tour centrale principale
    const coreGeo = new THREE.ConeGeometry(coreWidth / 2, coreHeight, 8);
    const coreMat = new THREE.MeshPhongMaterial({
      color: 0x0a1a3a,
      emissive: 0x00ffff,
      emissiveIntensity: 0.4,
      shininess: 150
    });
    const core = new THREE.Mesh(coreGeo, coreMat);
    core.position.set(0, coreHeight / 2, 0);
    core.castShadow = true;
    core.receiveShadow = true;
    this.scene.add(core);
    
    // Anneau luminescent au sommet
    const ringGeo = new THREE.TorusGeometry(coreWidth / 2 + 10, 3, 16, 100);
    const ringMat = new THREE.MeshPhongMaterial({
      color: 0x00ffff,
      emissive: 0x00ffff,
      emissiveIntensity: 0.8
    });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.position.set(0, coreHeight - 10, 0);
    ring.rotation.x = Math.PI / 2.5;
    ring.castShadow = true;
    this.scene.add(ring);
    
    // Sphère flottante au-dessus (nucleus)
    const nucleusGeo = new THREE.IcosahedronGeometry(15, 4);
    const nucleusMat = new THREE.MeshPhongMaterial({
      color: 0xff00ff,
      emissive: 0xff00ff,
      emissiveIntensity: 0.9,
      wireframe: false
    });
    const nucleus = new THREE.Mesh(nucleusGeo, nucleusMat);
    nucleus.position.set(0, coreHeight + 20, 0);
    nucleus.castShadow = true;
    this.scene.add(nucleus);
    
    // Animation de rotation du nucleus
    this.animateNucleus = () => {
      nucleus.rotation.x += 0.003;
      nucleus.rotation.y += 0.005;
    };
  }

  // ====== STREET LIGHTS ======
  createStreetLights() {
    const lightSpacing = 100;
    const gridCount = 10;
    
    for (let x = -gridCount; x < gridCount; x++) {
      for (let z = -gridCount; z < gridCount; z++) {
        const posX = x * lightSpacing;
        const posZ = z * lightSpacing;
        
        // Poteau
        const poleGeo = new THREE.CylinderGeometry(2, 2, 40, 8);
        const poleMat = new THREE.MeshPhongMaterial({ color: 0x222244 });
        const pole = new THREE.Mesh(poleGeo, poleMat);
        pole.position.set(posX, 20, posZ);
        pole.castShadow = true;
        this.scene.add(pole);
        
        // Lampe
        const lightGeo = new THREE.SphereGeometry(5, 8, 8);
        const lightColor = this.config.neonColors[Math.floor(Math.random() * this.config.neonColors.length)];
        const lightMat = new THREE.MeshPhongMaterial({
          color: lightColor,
          emissive: lightColor,
          emissiveIntensity: 0.8
        });
        const lamp = new THREE.Mesh(lightGeo, lightMat);
        lamp.position.set(posX, 38, posZ);
        lamp.castShadow = true;
        this.scene.add(lamp);
        
        // Lumière ponctuelle
        const pointLight = new THREE.PointLight(lightColor, 1.5, 200);
        pointLight.position.set(posX, 38, posZ);
        pointLight.castShadow = true;
        this.scene.add(pointLight);
        this.lights.push(pointLight);
      }
    }
  }

  // ====== PARTICLE EFFECTS ======
  createParticleEffects() {
    // Particules de poussière/énergie flottante
    const particleCount = 300;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    
    for (let i = 0; i < particleCount * 3; i += 3) {
      positions[i] = (Math.random() - 0.5) * 800;
      positions[i + 1] = Math.random() * 300;
      positions[i + 2] = (Math.random() - 0.5) * 800;
    }
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    const material = new THREE.PointsMaterial({
      color: 0x00aaff,
      size: 0.5,
      sizeAttenuation: true,
      transparent: true,
      opacity: 0.6
    });
    
    const particles = new THREE.Points(geometry, material);
    this.scene.add(particles);
    this.particleSystem = particles;
  }

  // ====== FLOATING ELEMENTS ======
  createFloatingElements() {
    // Petits drones/robots flottants
    for (let i = 0; i < 5; i++) {
      const droneGeo = new THREE.OctahedronGeometry(3, 1);
      const droneMat = new THREE.MeshPhongMaterial({
        color: 0x00ff88,
        emissive: 0x00ff88,
        emissiveIntensity: 0.7
      });
      const drone = new THREE.Mesh(droneGeo, droneMat);
      drone.position.set(
        (Math.random() - 0.5) * 300,
        50 + Math.random() * 150,
        (Math.random() - 0.5) * 300
      );
      
      drone.velocity = {
        x: (Math.random() - 0.5) * 2,
        y: (Math.random() - 0.5) * 0.5,
        z: (Math.random() - 0.5) * 2
      };
      
      this.particles.push(drone);
      this.scene.add(drone);
    }
  }

  // ====== LIGHTING ======
  setupLighting() {
    // Lumière ambiante
    const ambientLight = new THREE.AmbientLight(0x0066ff, 0.4);
    this.scene.add(ambientLight);
    
    // Lumière directionnelle (lune)
    const directionalLight = new THREE.DirectionalLight(0x0088ff, 0.6);
    directionalLight.position.set(100, 150, 100);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.left = -500;
    directionalLight.shadow.camera.right = 500;
    directionalLight.shadow.camera.top = 500;
    directionalLight.shadow.camera.bottom = -500;
    directionalLight.shadow.camera.far = 1000;
    this.scene.add(directionalLight);
    
    // Lumière rouge au sol (ambiance cyberpunk)
    const redLight = new THREE.PointLight(0xff0066, 0.3, 500);
    redLight.position.set(-150, 50, -150);
    this.scene.add(redLight);
  }

  // ====== UPDATE ======
  update() {
    // Animer le nucleus
    if (this.animateNucleus) {
      this.animateNucleus();
    }
    
    // Animer les drones
    this.particles.forEach(drone => {
      drone.position.x += drone.velocity.x;
      drone.position.y += drone.velocity.y;
      drone.position.z += drone.velocity.z;
      
      // Bounce
      if (drone.position.x > 250 || drone.position.x < -250) drone.velocity.x *= -1;
      if (drone.position.y > 250 || drone.position.y < 30) drone.velocity.y *= -1;
      if (drone.position.z > 250 || drone.position.z < -250) drone.velocity.z *= -1;
      
      // Rotation
      drone.rotation.x += 0.01;
      drone.rotation.y += 0.02;
    });
    
    // Pulse du nucleus
    if (this.nucleusLight) {
      this.nucleusLight.intensity = 1 + Math.sin(Date.now() * 0.002) * 0.5;
    }
  }

  // ====== SPAWNING AREAS ======
  getSpawnPoint(index = 0) {
    const spawnPoints = [
      { x: 0, y: 1.6, z: 30 },
      { x: -30, y: 1.6, z: 0 },
      { x: 30, y: 1.6, z: 0 },
      { x: 0, y: 1.6, z: -30 }
    ];
    return spawnPoints[index % spawnPoints.length];
  }

  getCollisionAreas() {
    // Retourner les zones de collision
    return this.buildings.map(b => ({
      center: b.position,
      radius: 50
    }));
  }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
  module.exports = NeoCity;
}
