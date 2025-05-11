import type { ValidLanguage } from '@/constants/languages';

export interface AboutTranslations {
  title: Record<ValidLanguage, string>;
  subtitle: Record<ValidLanguage, string>;
  whoWeAre: {
    title: Record<ValidLanguage, string>;
    content: Record<ValidLanguage, string>;
  };
  ourMission: {
    title: Record<ValidLanguage, string>;
    content: Record<ValidLanguage, string>;
  };
  whyChooseUs: {
    title: Record<ValidLanguage, string>;
    features: Record<ValidLanguage, string[]>;
  };
}

export const translations: AboutTranslations = {
  title: {
    fr: "À Propos",
    en: "About Us",
    ar: "من نحن"
  },
  subtitle: {
    fr: "Votre Guide de Pharmacies de Confiance",
    en: "Your Trusted Pharmacy Finder",
    ar: "دليلك الموثوق للصيدليات"
  },
  whoWeAre: {
    title: {
      fr: "Qui Sommes-Nous",
      en: "Who We Are",
      ar: "من نحن"
    },
    content: {
      fr: "Nous nous consacrons à vous aider à trouver des pharmacies de garde quand vous en avez le plus besoin. Notre plateforme vous connecte aux pharmacies disponibles dans différentes villes, facilitant l'accès aux services de santé essentiels 24h/24.",
      en: "We are dedicated to helping you find on-duty pharmacies when you need them most. Our platform connects you with available pharmacies across different cities, making it easier to access essential healthcare services 24/7.",
      ar: "نحن مكرسون لمساعدتك في العثور على الصيدليات المناوبة عندما تحتاج إليها. تربطك منصتنا بالصيدليات المتاحة في مختلف المدن، مما يسهل الوصول إلى الخدمات الصحية الأساسية على مدار الساعة."
    }
  },
  ourMission: {
    title: {
      fr: "Notre Mission",
      en: "Our Mission",
      ar: "مهمتنا"
    },
    content: {
      fr: "Fournir un service fiable et facile à utiliser qui aide les gens à localiser rapidement et efficacement les pharmacies ouvertes, particulièrement pendant les urgences et après les heures d'ouverture.",
      en: "To provide a reliable and easy-to-use service that helps people locate open pharmacies quickly and efficiently, especially during emergencies and after hours.",
      ar: "تقديم خدمة موثوقة وسهلة الاستخدام تساعد الناس في العثور على الصيدليات المفتوحة بسرعة وكفاءة، خاصة خلال حالات الطوارئ وبعد ساعات العمل."
    }
  },
  whyChooseUs: {
    title: {
      fr: "Pourquoi Nous Choisir",
      en: "Why Choose Us",
      ar: "لماذا تختارنا"
    },
    features: {
      fr: [
        "Mises à jour en temps réel sur la disponibilité des pharmacies",
        "Couverture dans plusieurs villes",
        "Interface facile à utiliser",
        "Information des pharmacies 24/7",
        "Données fiables et précises"
      ],
      en: [
        "Real-time updates on pharmacy availability",
        "Coverage across multiple cities",
        "Easy-to-use interface",
        "24/7 pharmacy information",
        "Reliable and accurate data"
      ],
      ar: [
        "تحديثات فورية عن توفر الصيدليات",
        "تغطية في العديد من المدن",
        "واجهة سهلة الاستخدام",
        "معلومات الصيدليات على مدار الساعة",
        "بيانات موثوقة ودقيقة"
      ]
    }
  }
}; 