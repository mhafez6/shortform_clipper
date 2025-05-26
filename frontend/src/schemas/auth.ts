import z from "zod";

export const signupSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z
    .string()
    .min(8, "Make your password longer, i don't care if it's secure"),
});

export type SignupFormValues = z.infer<typeof signupSchema>;
 