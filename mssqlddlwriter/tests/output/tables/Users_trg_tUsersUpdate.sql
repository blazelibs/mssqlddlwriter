-- created: 2011-06-03 03:23:22.757000
-- last updated: 2011-06-03 03:23:22.757000
--statement-break
SET ANSI_NULLS ON
--statement-break
SET QUOTED_IDENTIFIER ON

--statement-break
CREATE    TRIGGER [dbo].[tUsersUpdate]
ON [dbo].[Users]
FOR UPDATE
AS

DECLARE		@tabname	VARCHAR(100)
-- we would normally do something here, but this is just for testing