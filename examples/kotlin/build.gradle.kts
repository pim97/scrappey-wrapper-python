plugins {
    kotlin("jvm") version "1.9.0"
    application
}

repositories {
    mavenCentral()
}

application {
    mainClass.set("ExampleKt")
}

kotlin {
    jvmToolchain(11)
}
