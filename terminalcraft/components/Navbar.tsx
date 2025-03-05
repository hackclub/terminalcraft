"use client"

import { usePathname } from 'next/navigation'
import Image from 'next/image'
import Link from 'next/link'

export default function Navbar() {
  const pathname = usePathname()

  return (
    <header className="fixed top-0 left-0 z-100 pl-8">
      <Link
        href="https://hackclub.com"
        target="_blank"
        rel="noopener noreferrer"
        className="block"
      >
        <Image
          src="https://assets.hackclub.com/flag-orpheus-top.svg"
          alt="Hack Club"
          width={150}
          height={64}
          className="w-32 sm:w-25"
          priority
        />
      </Link>
    </header>
  )
} 