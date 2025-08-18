const catalogueUrl = 'http://localhost:8001/api/books/';
const empruntUrl = 'http://localhost:8002/api/loans/';

fetch(catalogueUrl).then(r=>r.json()).then(data=>{
  document.getElementById('livres').innerHTML = data.map(l=>`${l.titre} - ${l.auteur}`).join('<br>');
});

document.getElementById('formEmprunt').onsubmit = e => {
  e.preventDefault();
  fetch(empruntUrl + 'emprunter/', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({utilisateur_id:utilisateur_id.value, livre_id:livre_id.value})
  }).then(r=>r.json()).then(alert);
};