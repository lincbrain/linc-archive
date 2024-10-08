<template>
  <v-app-bar app>
    <v-menu
      v-if="$vuetify.breakpoint.mobile"
      open-on-hover
      offset-y
      close-delay="300"
    >
      <template #activator="{on}">
        <v-app-bar-nav-icon v-on="on" />
      </template>
      <v-list>
        <v-list-item-group>
          <template v-for="navItem in navItems">
            <v-list-item
              v-if="!navItem.if || navItem.if()"
              :key="navItem.text"
              :to="navItem.external ? undefined : {name: navItem.to}"
              :href="navItem.external ? navItem.to : undefined"
              :target="navItem.external ? '_blank' : undefined"
              :rel="navItem.external ? 'noopener' : undefined"
              @click.stop.prevent="navItem.onClick ? navItem.onClick() : null"
              exact
              text
            >
              <v-list-item-content
                v-if="!navItem.external"
                text
                class="text-md"
              >
                {{ navItem.text }}
              </v-list-item-content>
              <v-list-item-content
                v-if="navItem.external"
                :href="navItem.to"
                target="_blank"
                rel="noopener"
                text
              >
                {{ navItem.text }}
              </v-list-item-content>
              <v-icon
                v-if="navItem.external"
                class="ml-1"
                small
              >
                mdi-open-in-new
              </v-icon>
            </v-list-item>
          </template>
        </v-list-item-group>
      </v-list>
    </v-menu>
    <router-link to="/">
      <v-img
        alt="DANDI logo"
        contain
        width="100px"
        :src="logo"
        class="mr-3"
      />
    </router-link>
    <v-toolbar-items v-if="!$vuetify.breakpoint.mobile">
      <template v-for="navItem in navItems">
        <v-btn
          v-if="!navItem.external && (!navItem.if || navItem.if())"
          :key="navItem.text"
          :to="{name: navItem.to}"
          exact
          text
        >
          {{ navItem.text }}
        </v-btn>
        <v-btn
          v-if="navItem.external && (!navItem.if || navItem.if())"
          :key="navItem.text"
          :href="navItem.to"
          target="_blank"
          rel="noopener"
          text
        >
          {{ navItem.text }}
          <v-icon
            class="ml-1"
            small
          >
            mdi-open-in-new
          </v-icon>
        </v-btn>
      </template>
    </v-toolbar-items>

    <v-spacer />

    <div v-if="!insideIFrame">
      <template v-if="loggedIn">
        <div class="d-flex align-center">
          <v-btn
            :disabled="!user?.approved"
            :to="{ name: 'createDandiset' }"
            exact
            class="mx-3"
            color="#c44fc4"
            rounded
          >
            New Dataset
          </v-btn>
          <UserMenu />
        </div>
      </template>
      <template v-else>
        <v-tooltip
          bottom
          :disabled="cookiesEnabled"
        >
          <template #activator="{ on }">
            <div v-on="on">
              <v-btn
                id="login"
                class="mx-1"
                color="#c44fc4"
                rounded
                :disabled="!cookiesEnabled"
                @click="login"
              >
                Log In with GitHub
              </v-btn>
            </div>
          </template>
          <span>Enable cookies to log in.</span>
        </v-tooltip>
      </template>
    </div>
  </v-app-bar>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import {
  cookiesEnabled as cookiesEnabledFunc,
  loggedIn as loggedInFunc,
  insideIFrame as insideIFrameFunc,
  dandiRest,
  user,
} from '@/rest';
import {
  dandiAboutUrl, lincDocumentationUrl, lincHelpUrl, lincHubUrl, lincBrainUrl, lincWebKNOSSOSUrl
} from '@/utils/constants';
import UserMenu from '@/components/AppBar/UserMenu.vue';
import logo from '@/assets/linc-logo.svg';

interface NavigationItem {
  text: string,
  to: string,
  if?(): boolean,
  external: boolean,
  onClick?: () => void
}

const cookiesEnabled = computed(cookiesEnabledFunc);
const loggedIn = computed(loggedInFunc);
const insideIFrame = computed(insideIFrameFunc);

const navItems: NavigationItem[] = [
  {
    text: 'Shared Datasets',
    to: 'publicDandisets',
    external: false,
    if: loggedInFunc,
  },
  {
    text: 'My Datasets',
    to: 'myDandisets',
    external: false,
    if: loggedInFunc,
  },
    {
    text: 'Homepage',
    to: lincBrainUrl,
    external: true,
  },
  {
    text: 'Documentation',
    to: lincDocumentationUrl,
    external: true,
  },
  {
    text: 'Help',
    to: lincHelpUrl,
    external: true,
  },
  {
    text: 'JupyterHub',
    to: lincHubUrl,
    external: true,
  },
  {
    text: 'WebKNOSSOS',
    to: lincWebKNOSSOSUrl,
    external: true,
    onClick: () => {
      handleWebKNOSSOSClick();
    },
  },
];

function login() {
  dandiRest.login();
}

function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function waitForCookie(cookieName: string, timeout = 5000, interval = 100) {
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    // Log current document.cookie state for debugging
    console.log('Checking for cookie:', document.cookie);

    if (document.cookie.includes(`${cookieName}=`)) {
      console.log('Cookie found:', cookieName);
      return true; // Cookie found
    }
    await sleep(interval); // Wait and check again
  }

  console.log('Timeout: Cookie not found:', cookieName);
  return false; // Timeout occurred, cookie not found
}

async function handleWebKNOSSOSClick() {
  try {
    console.log('Attempting login to WebKNOSSOS...');
    const loginResponse = await dandiRest.loginWebKnossos();

    // Log login response to ensure it's complete
    console.log('Login response received:', loginResponse);

    // Poll for the cookie named 'id' with a 5-second timeout and 100ms intervals
    const cookieSet = await waitForCookie('id', 10000); // Extend timeout to 10 seconds for robustness

    if (cookieSet) {
      console.log('Opening WebKNOSSOS...');
      window.open(lincWebKNOSSOSUrl, '_blank');
    } else {
      console.error('Login to WebKNOSSOS did not populate the cookie within the timeout.');
    }
  } catch (error) {
    console.error('Login to WebKNOSSOS failed:', error);
  }
}
</script>
