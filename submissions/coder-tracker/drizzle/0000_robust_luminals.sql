CREATE TABLE `goals` (
	`id` text PRIMARY KEY NOT NULL,
	`name` text NOT NULL,
	`finished` integer DEFAULT false NOT NULL,
	`user_id` text NOT NULL,
	`session_id` text
);
--> statement-breakpoint
CREATE TABLE `notifications` (
	`id` text PRIMARY KEY NOT NULL,
	`user_id` text NOT NULL,
	`message` text NOT NULL,
	`read` integer DEFAULT false NOT NULL,
	`timestamp` integer NOT NULL
);
--> statement-breakpoint
CREATE TABLE `sessions` (
	`id` text PRIMARY KEY NOT NULL,
	`name` text NOT NULL,
	`finished` integer DEFAULT false NOT NULL,
	`start` integer NOT NULL,
	`duration` integer NOT NULL,
	`actual_duration` integer,
	`procrastination_duration` integer DEFAULT 0 NOT NULL,
	`files` text,
	`user_id` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `users` (
	`id` text PRIMARY KEY NOT NULL,
	`xp` integer DEFAULT 0 NOT NULL,
	`resets` integer DEFAULT 0 NOT NULL,
	`unlocks` blob DEFAULT '{"type":"Buffer","data":[0,0,0,0,0,0,0,0,0,0]}' NOT NULL,
	`active_theme` integer,
	`active_badge` integer,
	`active_session_id` text
);
