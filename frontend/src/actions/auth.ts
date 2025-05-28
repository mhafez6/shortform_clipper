"use server";

import { hashPassword } from "~/lib/auth";
import { signupSchema, type SignupFormValues } from "~/schemas/auth";
import { db } from "~/server/db";

type SignupResult = {
  success: boolean;
  error?: string;
};

export async function signUp(data: SignupFormValues): Promise<SignupResult> {
  const validationResult = signupSchema.safeParse(data);
  if (!validationResult.success) {
    return {
      success: false,
      error: validationResult.error.issues[0]?.message ?? "wrong input",
    };
  }
  const { email, password } = validationResult.data;

  try {
    const existingUser = await db.user.findUnique({ where: { email } });
    if (existingUser) {
      return {
        success: false,
        error: "email alreay in use",
      };
    }
    const hashedPassword = await hashPassword(password);

    // add lemon squeezy stuff later, cosnt lemonsquuezy id or whatever

    await db.user.create({
      data: {
        email,
        password: hashedPassword,
      },
    });

    return { success: true };
  } catch (_error) {
    return { success: false, error: "idk but something went wrong" };
  }
}
