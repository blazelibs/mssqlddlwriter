-- created: 2011-06-03 02:42:40.273000
-- last updated: 2011-06-03 02:42:40.283000

--statement-break
CREATE TABLE dbo.[Users] (
	[UserID] INTEGER NOT NULL IDENTITY(1,1),
	[UserGUID] UNIQUEIDENTIFIER NULL DEFAULT (newid()),
	[UserLogin] VARCHAR(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL DEFAULT (newid()),
	[UserName] VARCHAR(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	[SecurityLevel] INTEGER NULL,
	[Created] DATETIME NOT NULL DEFAULT (getdate()),
	[LastModified] DATETIME NULL,
	[Active] BIT NOT NULL DEFAULT ((1)),
	associate_id INTEGER NULL,
	pass_hash VARCHAR(128) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL DEFAULT ('placeholder'),
	PRIMARY KEY ([UserID]),
	CONSTRAINT [FK_Users_Associates] FOREIGN KEY(associate_id) REFERENCES dbo.[Associates] ([AssociateID]) ON DELETE CASCADE
)

--statement-break
ALTER TABLE [dbo].[Users] ADD CONSTRAINT [IX_UserLogin] UNIQUE ([UserLogin] ASC) ON [PRIMARY]

--statement-break
ALTER TABLE [dbo].[Users] ADD CONSTRAINT [CK_Users_AssociateId] CHECK (([associate_id]>(1000)))

--statement-break
CREATE NONCLUSTERED INDEX [AssociateId] ON [dbo].[Users] ([associate_id] ASC, [UserID] DESC, [Active] ASC) ON [PRIMARY]
