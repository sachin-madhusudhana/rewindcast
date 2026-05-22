'use client';

import Link from 'next/link';

export function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link href="/" className="navbar-logo">
          <span>⏪</span> RewindCast
        </Link>
        <ul className="navbar-links">
          <li><Link href="/#how-it-works">How it Works</Link></li>
          <li><Link href="/#try-it">Try It</Link></li>
          <li>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
          </li>
        </ul>
      </div>
    </nav>
  );
}
