import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import AboutSection from "@/components/AboutSection";
import SpeakersSection from "@/components/SpeakersSection";
import ScheduleSection from "@/components/ScheduleSection";
import VenueSection from "@/components/VenueSection";
import TestimonialsSection from "@/components/TestimonialsSection";
import FAQSection from "@/components/FAQSection";
import RegisterSection from "@/components/RegisterSection";
import Footer from "@/components/Footer";
import ScrollToTop from "@/components/ScrollToTop";

const Index = () => {
  return (
    <div className="min-h-screen overflow-x-hidden">
      <Navbar />
      <HeroSection />
      <AboutSection />
      <SpeakersSection />
      <ScheduleSection />
      <VenueSection />
      <TestimonialsSection />
      <FAQSection />
      <RegisterSection />
      <Footer />
      <ScrollToTop />
    </div>
  );
};

export default Index;