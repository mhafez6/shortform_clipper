"use server";
/* eslint-disable @typescript-eslint/no-unsafe-call */

import { S3Client } from "@aws-sdk/client-s3";
import { env } from "~/env";
import { auth } from "~/server/auth";
import { v4 as uuidv4 } from "uuid";

export async function generateUploadUrl(fileInfo: {
  filename: string;
  contentType: string;
}): Promise<{ success: boolean }> {
  const session = await auth();
  if (!session) throw new Error("unauthorized");

  const s3Client = new S3Client({
    region: env.AWS_REGION,
    credentials: {
      accessKeyId: env.AWS_ACCESS_KEY_ID,
      secretAccessKey: env.AWS_SECRET_ACCESS_KEY,
    },
  });

  const fileExtension = fileInfo.filename.split(".").at(-1) ?? "";

  const uniqueId = uuidv4() as string;
  const key = `${uniqueId}`;
}
