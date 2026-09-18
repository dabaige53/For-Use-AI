const paths = {
 gear:'<path fill="currentColor" stroke="none" d="m10 1 4 0 .6 3 2 .9 2.6-1.5 2 3.4-2.2 2v2.4l2.2 2-2 3.5-2.7-.9-2 1-.5 3.2h-4l-.6-3.2-2-1-2.7.9-2-3.5 2.3-2V9L2.8 7l2-3.4L7.5 5l2-.9z"/><circle cx="12" cy="10.8" r="3.5" fill="white" stroke="none"/>',
 more:'<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
 link:'<path d="m10 14 4-4M8 16l-2 2a4 4 0 0 1-6-6l5-5a4 4 0 0 1 6 0M16 8l2-2a4 4 0 0 1 6 6l-5 5a4 4 0 0 1-6 0" transform="translate(2 0) scale(.85)"/>',
 down:'<path d="m6 9 6 6 6-6"/>',

 book:'<path d="M4 4h6a3 3 0 0 1 3 3v14a4 4 0 0 0-4-3H4zM20 4h-4a3 3 0 0 0-3 3v14a4 4 0 0 1 4-3h3z"/>',
 search:'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
 copy:'<rect x="8" y="8" width="12" height="13" rx="2"/><path d="M16 8V4a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h4"/>',
 list:'<path d="M8 5h13M8 12h13M8 19h13M3 5h.01M3 12h.01M3 19h.01"/>',
 menu:'<path d="M4 6h16M4 12h16M4 18h16"/>',
 close:'<path d="m6 6 12 12M18 6 6 18"/>',
 question:'<circle cx="12" cy="12" r="9"/><path d="M9 9a3 3 0 0 1 6 0c0 2-3 2-3 5M12 17h.01"/>',
 brain:'<path d="M12 5c-3-5-8-1-6 3-5 1-4 7 0 7-2 5 4 8 6 4 2 4 8 1 6-4 4 0 5-6 0-7 2-4-3-8-6-3v14M6 8l3 2M18 8l-3 2M6 15l3-2M18 15l-3-2"/>',
 flow:'<rect x="3" y="3" width="6" height="6" rx="1"/><rect x="15" y="15" width="6" height="6" rx="1"/><path d="M6 9v9h9M9 6h9v9"/>',
 chat:'<path d="M4 4h16v12H9l-5 4zM8 8h8M8 12h5"/>',
 check:'<rect x="4" y="3" width="16" height="18" rx="2"/><path d="m8 12 3 3 5-6"/>',
 compass:'<circle cx="12" cy="12" r="9"/><path d="m16 8-2 6-6 2 2-6z"/>',
 layers:'<path d="m12 3 10 5-10 5L2 8zM2 12l10 5 10-5M2 16l10 5 10-5"/>'
};
export const icon = (name) => `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name] || paths.book}</svg>`;
