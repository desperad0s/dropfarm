import React from 'react'
import Link from 'next/link'
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

interface UserAvatarProps {
  username: string
  imageUrl?: string
}

export function UserAvatar({ username, imageUrl }: UserAvatarProps) {
  return (
    <Link href="/profile">
      <Avatar>
        <AvatarImage src={imageUrl} alt={username} />
        <AvatarFallback>{username[0].toUpperCase()}</AvatarFallback>
      </Avatar>
    </Link>
  )
}