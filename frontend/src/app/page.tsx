import Link from "next/link";
import { Button } from "~/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { ThemeToggle } from "~/components/theme-toggle";
import {
  Video,
  ArrowRight,
  Upload,
  Scissors,
  Download,
  Mic,
  Users,
  Zap,
} from "lucide-react";

export default function HomePage() {
  return (
    <div className="bg-background min-h-screen">
      {/* Navigation - Matching Dashboard Style */}
      <header className="bg-background sticky top-0 z-10 flex justify-center border-b">
        <div className="container flex h-16 items-center justify-between px-4 py-2">
          <Link href="/" className="flex items-center">
            <div className="font-sans text-xl font-medium tracking-tight">
              <span className="text-foreground">Shortform</span>
              <span className="font-light text-gray-500">/</span>
              <span className="text-foreground font-light">Clipper</span>
            </div>
          </Link>
          <div className="flex items-center space-x-4">
            <ThemeToggle />
            <Link href="/login">
              <Button variant="ghost">Sign In</Button>
            </Link>
            <Link href="/signup">
              <Button>Get Started</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-24">
        <div className="mx-auto max-w-3xl text-center">
          <h1 className="mb-6 text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
            Turn Long Videos Into
            <span className="text-primary"> Viral Clips</span>
          </h1>
          <p className="text-muted-foreground mx-auto mb-8 max-w-2xl text-lg">
            Upload your podcasts or long videos and let AI automatically extract
            the most engaging moments into shareable clips.
          </p>
          <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
            <Link href="/signup">
              <Button size="lg" className="w-full sm:w-auto">
                Start Creating Clips
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="outline" size="lg" className="w-full sm:w-auto">
                View Demo
              </Button>
            </Link>
          </div>
        </div>
      </main>

      {/* AI Features */}
      <section className="container mx-auto px-4 py-16">
        <div className="mx-auto max-w-4xl">
          <h2 className="mb-12 text-center text-2xl font-semibold">
            AI-Powered Features
          </h2>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader>
                <Mic className="text-primary mb-2 h-8 w-8" />
                <CardTitle className="text-lg">
                  Active Speaker Detection
                </CardTitle>
                <CardDescription>
                  AI identifies when speakers are talking and creates vertical
                  clips optimized for social media
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <Users className="text-primary mb-2 h-8 w-8" />
                <CardTitle className="text-lg">Multi-Speaker Support</CardTitle>
                <CardDescription>
                  Automatically detects and tracks multiple speakers in
                  conversations and interviews
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <Zap className="text-primary mb-2 h-8 w-8" />
                <CardTitle className="text-lg">
                  Smart Moment Detection
                </CardTitle>
                <CardDescription>
                  AI finds the most engaging moments and creates clips with
                  perfect timing
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="container mx-auto px-4 py-16">
        <div className="mx-auto max-w-4xl">
          <h2 className="mb-12 text-center text-2xl font-semibold">
            How it works
          </h2>
          <div className="grid gap-8 md:grid-cols-3">
            <div className="text-center">
              <div className="bg-primary/10 mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full">
                <Upload className="text-primary h-6 w-6" />
              </div>
              <h3 className="mb-2 font-medium">Upload</h3>
              <p className="text-muted-foreground text-sm">
                Drop your video file
              </p>
            </div>
            <div className="text-center">
              <div className="bg-primary/10 mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full">
                <Scissors className="text-primary h-6 w-6" />
              </div>
              <h3 className="mb-2 font-medium">AI Processing</h3>
              <p className="text-muted-foreground text-sm">
                AI finds the best moments
              </p>
            </div>
            <div className="text-center">
              <div className="bg-primary/10 mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full">
                <Download className="text-primary h-6 w-6" />
              </div>
              <h3 className="mb-2 font-medium">Download</h3>
              <p className="text-muted-foreground text-sm">
                Get your viral clips
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
