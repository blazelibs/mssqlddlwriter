SET ANSI_NULLS ON
--statement-break
SET QUOTED_IDENTIFIER ON
--statement-break
SET ANSI_PADDING ON

--statement-break
CREATE TABLE [dbo].[Associates](
	[AssociateID] [int] IDENTITY(1,1) NOT NULL PRIMARY KEY,
	[AssociateName] [varchar](55) NOT NULL
)

--statement-break
CREATE TABLE [dbo].[Users](
	[UserID] [int] IDENTITY(1,1) NOT NULL,
	[UserGUID] [uniqueidentifier] NULL DEFAULT (newid()),
	[UserLogin] [varchar](50) NOT NULL DEFAULT (newid()),
	[UserName] [varchar](50) NULL,
	[SecurityLevel] [int] NULL,
	[Created] [datetime] NOT NULL DEFAULT (getdate()),
	[LastModified] [datetime] NULL,
	[Active] [bit] NOT NULL DEFAULT (1),
	[associate_id] [int] NULL,
	[pass_hash] [varchar](128) NOT NULL DEFAULT ('placeholder'),
        CONSTRAINT [PK_Users] PRIMARY KEY CLUSTERED
       (
               [UserID] ASC
       )WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON, FILLFACTOR = 80) ON [PRIMARY],
        CONSTRAINT [IX_UserLogin] UNIQUE NONCLUSTERED
       (
               [UserLogin] ASC
       )WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON, FILLFACTOR = 80) ON [PRIMARY]
) ON [PRIMARY]

--statement-break
SET ANSI_PADDING OFF
--statement-break
ALTER TABLE [dbo].[Users]  WITH NOCHECK ADD  CONSTRAINT [FK_Users_Associates] FOREIGN KEY([associate_id])
REFERENCES [dbo].[Associates] ([AssociateID])
ON DELETE CASCADE
--statement-break
ALTER TABLE [dbo].[Users] CHECK CONSTRAINT [FK_Users_Associates]

